#-*-coding: utf8 -*-
'''
Created on Aug 25, 2017

@author: Tiangang Yin
@author: Florian de Boissieu: contribution to format specification and extra bytes integration.
@author: Grégoire Couderc : contribution to format specification.
'''

import sys
import struct
import math
import argparse
import laspy
import numpy as np
from .GaussianDecomposition import *
from gdecomp import GaussianDecomposition

speedOfLightPerNS=0.299792458

hearder_length=90            # 50+12+28
waveform_parameter_length=104 #
min_amp=1

hearder_format="=50s2I4?2d3I"
waveform_parameter_format="=11d4I"
to8bit_format="=b"

evlr_wave_header_length = 60
evlr_wave_format = "<1H16s1HQ32s"

MINAMP = 1


class DART2LAS(object):
    '''
    Class to convert DART full-waveform lidar simulation binary files to LAS.

    It support all LAS 1.4 formats including waveforms, point clouds and extrabytes (width, amplitude of gaussian decomposition)

    Class variables:
        self.lasFormat: int
            LAS formats, see LAS 1.4 documentation.
        self.typeOut: int
            - 1: Peak amplitude of the Gaussian profile, intensity = A/sigma with waveform=A/(sigma*sqrt(2*PI))*e^((t-u)/sigma^2)
            - 2: Integral of the Gaussian profile, intensity = A
            - 3: Standard deviation of the Gaussian profile, intensity = sigma * 10.0 #To avoid small values
            - 4 (default): Intensity in the RIEGL way: intensity = I, with waveform=I*e^((t-u)/sigma^2)
        self.ifFixedGain: bool
            If True self.fixedGain is taken into account
        self.fixedGain: float
        TODO: complete documentation
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.ifFixedGain = False
        self.typeOut = 4 # Default to output integration of decomposed Gaussian profile
        self.fixedGain = 1.0
        self.receiveWaveOffset = 0
        self.waveNoiseThreshold = 2
        self.maxOutput = 127 
        self.ifSolarNoise = False
        self.snFile = 'solar_noise.txt'
        self.snMap = [[0.0]]
        self.ifOutputImagePerBin = False
        self.imagePerBinPath = '~/'
        self.ifOutputNbPhotonPerPulse = False
        self.txtNbPhotonPerPulse = 'nbPhotonPerPulse.txt'
        self.txtNbPhotonMap = [[0.0]]
        self.containerImagePerBin = [[[0.0]]]
        self.ifWriteWaveform = False
        self.lasFormat = None
        self.lasVersion = None
        self.minimumIntensity = 1 # sensor lower detection threshold. There should also be a maximumDetectionThreshold
        self.extra_bytes = True # if True writes the Pulse width and Amplitude as RIEGL Extra Bytes

        ### available formats
        ### difference between 1 and 6 (or 4 and 9) is the number of bits in Return Number (see LAS v1.4 specs)
        # echos only:  1, 6 -> XYZIRNSECAUPT
        # echos and waveform:  4, 9 -> XYZIRNSECAUPTWpBWfpRpwlXtYtZt


        
        self.scale = 0.001
        self.prf = 500000.0 # pulse rate
        self.byteOption = 1 # False for 8 bits to represent waveform amplitude, True for 16 bits to represent waveform amplitude
        self.nbBytePerWaveAmplitude = 2
        self.waveformAmplitudeFomat = 'H'
        
    def readSolarNoiseFile(self):
        print('reading solar noise file: ',self.snFile)
        with open(self.snFile,'r') as f:
            for row in f.readlines():
                content=row.split()
                self.addToSnMap(int(content[0]), int(content[1]), float(content[5]))
    
    def addToSnMap(self, indX, indY, snValue):
        if len(self.snMap)<indX+1:
            for i in range(len(self.snMap),indX+1):
                self.snMap.append([0.0])
        if len(self.snMap[indX])<indY+1:
            for i in range(len(self.snMap[indX]),indY+1):
                self.snMap[indX].append([0.0])
        self.snMap[indX][indY]=snValue
    
    def readDARTBinaryFileAndConvert2LAS(self, dartFileName, lasFileName):
        """
        Convert a DART binary file to LAS

        Parameters
        ----------
        dartFileName: str
        lasFileName: str

        Returns
        -------
        (float, float)
        digitizer_offset and digitizer_gain
        """

        if self.lasFormat is None:  # set default format if empty
            if self.ifWriteWaveform:
                self.lasFormat = 4
            else:
                self.lasFormat = 1
        else:  # check format if not empty
            if (self.ifWriteWaveform and (self.lasFormat not in [4, 5, 9, 10])) or (
                    (not self.ifWriteWaveform) and (self.lasFormat in [4, 5, 9, 10])):
                raise ValueError("LAS format not coherent with ifWriteWaveform:\n"
                                 "ifWriteWaveform must be True for formats 4, 5, 9 or 10"
                                 "Other formats are not supported at the moment.")

        if self.lasVersion is None:
            self.lasVersion = 1.3
        else:
            if self.lasVersion < 1.3:
                print("Error: LAS version not available")
                exit()
            if self.lasFormat > 5 and self.lasVersion == 1.3:
                print("Error: LAS format not available for LAS version 1.3")
                exit()

        print("LAS format: " + str(self.lasFormat))

        if self.ifSolarNoise:
            self.readSolarNoiseFile()
            
################## READING DART FILE#################


        # DART Header
        dartfile = open(dartFileName, "rb")   ###DART file
        
        try:
            hearder_record = dartfile.read(hearder_length)
        except:
            tb = sys.exc_info()[2]
            print("Reading failed on input DART file " + dartFileName + "\n")
            sys.exit(1)
        header_data=struct.unpack(hearder_format,hearder_record)
        print("Input Data Information:")
        print("  Version: ", header_data[0][0:42])    
        #Parameters about the locations of the waveform record
        ifFormatFloat=header_data[3]
        ifExistNonConv=header_data[4]
        ifExistFirstOrder=header_data[5]
        ifExistStats=header_data[6]

        nbBinsConvolved=header_data[9]
        nbBinsNonConvolved=header_data[10]

        #Calculate the offset of waveforms between pulses
        posOffsetPerPulse=0
        nbBytes=8
        waveIterFormat="=%dd"
        if ifFormatFloat:
            nbBytes=4
            waveIterFormat="=%df"

        if ifExistStats:
            posOffsetPerPulse+=9+41*nbBytes-1
        if ifExistNonConv:
            if ifExistFirstOrder:
                posOffsetPerPulse+=nbBytes*(2*nbBinsNonConvolved+nbBinsConvolved)
            else:
                posOffsetPerPulse+=nbBytes*nbBinsNonConvolved
        else:
            if ifExistFirstOrder:
                posOffsetPerPulse+=nbBytes*nbBinsConvolved

        convolved_Length=nbBytes*nbBinsConvolved  #The length of convolved waveform data in bytes

        #Pulse Global Parameters:
        timeStep_in_nano_second=header_data[7]
        timeStep_in_pico_second=timeStep_in_nano_second * 1000.0
        distStep=header_data[8]
        print("timeStep_in_nano_second", timeStep_in_nano_second)
        nbPulses=header_data[11]
        print('Total number of pulses: ',nbPulses)
        
        

            
        if self.ifWriteWaveform:
            #Waveform Output file Header
            if self.byteOption == 0: # For 8 bit representative
                self.nbBytePerWaveAmplitude = 1 
                self.waveformAmplitudeFomat = 'B'
            
            waveformfile = open(lasFileName[:-4]+'.wdp', 'wb')
            #format definition
            reserve_evlr_wave = 0
            user_id_evlr_wave = b'LASF_Spec       '
            record_id_evlr_wave = 65535
            record_len_aft_header_evlr_wave = nbBinsConvolved * self.nbBytePerWaveAmplitude * nbPulses
            description_evlr_wave = b'Waveform Data Packets           '
            header_packed = struct.pack(evlr_wave_format, reserve_evlr_wave, user_id_evlr_wave, record_id_evlr_wave, record_len_aft_header_evlr_wave, description_evlr_wave)
            if not len(header_packed) == evlr_wave_header_length:
                print('Error: waveform file header length not satisifed!!!')
                exit()
            waveformfile.write(header_packed)
            off_waveformfile = waveformfile.tell()
            print('off_waveformfile', off_waveformfile)

        #read and convert parameters:

        tmp = dartfile.tell()

#         outPulses = list()
        feedback = int(nbPulses/10.0)
        countPulses = 0
        pulsesInBuffer = 0

        tmpIndicatorPast = 0

        # points vectors
        x_v=[]
        y_v=[]
        z_v=[]
        intensity_v=[]
        return_num_v=[]
        num_returns_v=[]
        scan_angle_rank_v=[] # format 1-5: 1 byte integer in range [-90,90] degrees (see LAS 1.4 specifications)
        scan_angle_v=[] # format 6-10: 2 bytes integer with increment equivalent to 0.006 degree.
        ANGLE_INC = 0.006 # angle increment for LAS 1.4 format 6-10
        gpstime_v=[]

        # Extra Bytes vectors
        pulse_width_v = []
        amplitude_v = []

        # Waveform vectors
        wave_packet_desc_index_v=[]  # to be replaced to an array of ones at the end
        byte_offset_to_waveform_data_v=[]
        waveform_packet_size_v=[]
        return_point_waveform_loc_v=[]
        x_t_v=[]
        y_t_v=[]
        z_t_v=[]
        
        receiveWaveGain = 1

        if (self.ifFixedGain):
            receiveWaveGain=float(self.fixedGain)
            print('Defined gain: ', receiveWaveGain)
        else:
            #Generally compute the proper gain
            #Make a copy of the current position, go through the waveform values for a statistical distribution of the waveform amplitude
            waveMax = -1
            tmp2 = dartfile.tell()
            for cnt in range(nbPulses):
                dartfile.seek(tmp2+waveform_parameter_length)
                try:
                    wave = dartfile.read(convolved_Length)
                except:
                    tb = sys.exc_info()[2]
                    raise IOError("Reading failed on input DART LIDARIMAGE file while reading waveform of each pulse" + dartFileName, tb)
                wave_data = np.array(struct.unpack(waveIterFormat %nbBinsConvolved, wave))
#                 wave_data_nonzero = [val for val in wave_data if val > 0.0];
                tmpMax = wave_data.max()
                if tmpMax>waveMax:
                    waveMax = tmpMax
                tmp2 = dartfile.tell()    
                tmp2 += posOffsetPerPulse
            if not waveMax > 0:
                print('Error: Cannot find the wave maximum, please define a gain')
                exit()
            receiveWaveGain=float(self.maxOutput)/waveMax
            print('Calculated gain according to maximum normalization: ', receiveWaveGain)

        print("nbPulses: {}".format(nbPulses))
        import time
        start = time.time()
        print('start time: {}'.format(start))
        for cnt in range(nbPulses):
            dartfile.seek(tmp)
            try:
                pulseInfo = dartfile.read(waveform_parameter_length)
            except:
                tb = sys.exc_info()[2]
                raise IOError("Reading failed on input DART LIDARIMAGE file while reading parameter of each pulse" + dartFileName, tb)
            #end try
            pulse_info=struct.unpack(waveform_parameter_format, pulseInfo)
            try:
                wave = dartfile.read(convolved_Length)
            except:
                tb = sys.exc_info()[2]
                raise IOError("Reading failed on input DART LIDARIMAGE file while reading waveform of each pulse" + dartFileName, tb)
            #end try
            wave_data = np.array(list(struct.unpack(waveIterFormat %nbBinsConvolved, wave)))
            if any(wave_data>0):
                y_decomp = (wave_data * receiveWaveGain).astype(int)
                if any(y_decomp > 0):
                    y_decomp[y_decomp > self.maxOutput] = self.maxOutput
                    # for i in range(nbBinsConvolved):
                    #     c=int(wave_data[i]*receiveWaveGain)  #approximated count < 128
                    #     if c>self.maxOutput:
                    #         c=self.maxOutput
                    #     y_decomp.append(c)

                    if (self.ifOutputNbPhotonPerPulse):
                        sum_wave_data = 0
                        for j in range(len(wave_data)):
                            sum_wave_data += wave_data[j]
                        self.addToNbPhotonPerPulseMap(pulse_info[12], pulse_info[13], sum_wave_data);

        #             #ajust the gain and output regarding automatic gain control per pulse.
        #             maxCount=1e-8
        #             for j in range(len(wave_data)):
        #                 if self.ifSolarNoise:
        #                     wave_data[j]+=self.snMap[pulse_info[12]][pulse_info[13]]
        #                 if not wave_data[j] == 0.0 and wave_data[j]>maxCount:
        #                     maxCount=wave_data[j]
        #
        #             if maxCount==1e-8:
        #                 tmp = dartfile.tell() #saves current position in input file before jump to the data of the next waveform
        #                 tmp += posOffsetPerPulse
        #                 continue
        #
        #             if (maxCntGlobe<maxCount):
        #                 maxCntGlobe=maxCount


                    nbBinsToCenterFOV = pulse_info[11]
                    distToCenterFOV = nbBinsToCenterFOV*distStep

                    distToBeginWave=distToCenterFOV+speedOfLightPerNS*pulse_info[9] #pulse_info[10] is negative

                    #!!!!!!!!!!!!!!!!!!Making the vector looking upward (z_t>0) for ALS device to keep consistent with LAS format
                    # see https://github.com/ASPRSorg/LAS/wiki/Waveform-Data-Packet-Descriptors-Explained
                    x_t = -pulse_info[3]
                    y_t = -pulse_info[4]
                    z_t = -pulse_info[5]

                    x0_abs = pulse_info[6] - x_t/2*distToBeginWave #Divided by 2 change from distance to waveform (2 way)
                    y0_abs = pulse_info[7] - y_t/2*distToBeginWave
                    z0_abs = pulse_info[8] - z_t/2*distToBeginWave

                    # gpsTime = float(pulse_info[14]) / self.prf
                    gpsTime = float(pulse_info[14]) # pulse ID (0-based)

                    scan_angle_rank = int(round(pulse_info[0]))
                    scan_angle = int(round(pulse_info[0]/ANGLE_INC))

                    x_per_bin = x_t * distStep / 2
                    y_per_bin = y_t * distStep / 2
                    z_per_bin = z_t * distStep / 2


                    if self.ifWriteWaveform:
                        x_t_pico_second = x_per_bin / timeStep_in_pico_second
                        y_t_pico_second = y_per_bin / timeStep_in_pico_second
                        z_t_pico_second = z_per_bin / timeStep_in_pico_second
                        currentWritingPosWave = waveformfile.tell()


                    # y_decomp_arr = np.array(y_decomp)
                    y_decomp_arr = y_decomp
                    # indexes_peaks = findZeroCrossingPeaks(y_decomp_arr, self.waveNoiseThreshold)

                    ###Gaussian Decomposition
                    # if len(indexes_peaks)>0:
                        # in_x = np.array(range(len(y_decomp)))+0.5 ## commented on C++ binding of Gaussian Decomposition
                        # out = gaussian_decomposition(in_x, y_decomp_arr, indexes_peaks) ## commented on C++ binding of Gaussian Decomposition
                    out = GaussianDecomposition(y_decomp_arr.astype(float), float(self.waveNoiseThreshold), 3)
                    # if cnt in [949, 950]:
                    #     indexes_peaks = findZeroCrossingPeaks(y_decomp_arr, self.waveNoiseThreshold)
                    #     in_x = np.array(range(len(y_decomp))) ## commented on C++ binding of Gaussian Decomposition
                    #     out = gaussian_decomposition(in_x, y_decomp_arr, indexes_peaks) ## commented on C++ binding of Gaussian Decomposition
                    #     out = np.reshape(out, (-1,3))
                    #     in_x = np.array(range(len(y_decomp)))
                    #     fit = np.zeros(y_decomp_arr.size)
                    #     for i in range(out.shape[0]):
                    #         fit += out[i,0] * np.exp(-(in_x - out[i,1])**2 / (2 * out[i,2]**2))
                    #     plt.clf()
                    #     plt.plot(in_x, y_decomp_arr, color='b')
                    #     plt.plot(in_x, fit, color='r')
                    #     plt.show()

                    # if out.success: ## commented on C++ binding of Gaussian Decomposition
                    if len(out)>0:
                        out = np.reshape(out, (-1,3))
                        out = out[out[:,0]>0, :] # amplitude 0 can occure, e.g. cnt=949
                        # print len(out.best_values)/3, out.best_values['g0_amplitude']
                        if self.ifWriteWaveform:
                            for c in y_decomp:
                                waveformfile.write(struct.pack('<'+self.waveformAmplitudeFomat,c))
                        countPulses+=1
                        pulsesInBuffer+=1
                        # nbPointsDecomp = len(out.best_values)//3 ## commented on C++ binding of Gaussian Decomposition
                        nbPointsDecomp = out.shape[0]

                        for i in range(nbPointsDecomp):
                            # ptsPrefix = 'g' + str(i) + '_'
                            # ptsAmp = out.best_values[ptsPrefix+'amplitude'] ## commented on C++ binding of Gaussian Decomposition
                            # ptsSigma = out.best_values[ptsPrefix+'sigma'] ## commented on C++ binding of Gaussian Decomposition
                            # ptsCenter = out.best_values[ptsPrefix+'center'] ## commented on C++ binding of Gaussian Decomposition
    #                         print ptsAmp,   ptsCenter, x0, y0, z0, x_t, y_t, z_tout[i, 1]
                            ptsAmp = out[i, 0]
                            ptsSigma = out[i, 2]
                            ptsCenter = out[i, 1]+0.5
                            x_abs = x0_abs - x_per_bin*ptsCenter
                            y_abs = y0_abs - y_per_bin*ptsCenter
                            z_abs = z0_abs - z_per_bin*ptsCenter

                            if self.typeOut == 1:  # Peak amplitude of the Gaussian profile
                                intensity = ptsAmp/ptsSigma
                            elif self.typeOut == 2:# Integral of the Gaussian profile
                                intensity = ptsAmp
                            elif self.typeOut == 3:# Standard deviation of the Gaussian profile
                                intensity = ptsSigma * 10.0 #To not making the value too small
                            elif self.typeOut == 4: # Intensity in the RIEGL way: waveform=I*e^((t-u)/sigma^2)
                                intensity = ptsAmp / (ptsSigma * math.sqrt(2 * math.pi))
                            else:
                                print('Error: the output type option is not supported')
                                quit()


                            # All formats variables
                            # xyz are scaled inside las object
                            # x_v.append(int(round( x_abs / self.scale)))
                            # y_v.append(int(round( y_abs / self.scale)))
                            # z_v.append(int(round( z_abs / self.scale)))
                            x_v.append(x_abs)
                            y_v.append(y_abs)
                            z_v.append(z_abs)
                            intensity_v.append(intensity)
                            if self.lasFormat in range(6, 11):
                                scan_angle_v.append(scan_angle)
                            else:
                                scan_angle_rank_v.append(scan_angle_rank)
                            gpstime_v.append(gpsTime)
                            return_num_v.append(i+1)
                            num_returns_v.append(nbPointsDecomp)


                            # Extra Bytes
                            if self.extra_bytes:
                                pulse_width_v.append(ptsSigma * (2 * math.sqrt(2 * math.log(2)))) # Full Width at Half Maximum
                                # print('{} {} {} {}'.format(cnt, ptsAmp, intensity, ptsSigma))
                                amplitude_v.append(10*math.log10(intensity/self.minimumIntensity))

                            # Waveform
                            if self.ifWriteWaveform:
                                byte_offset_to_waveform_data_v.append(currentWritingPosWave)
                                waveform_packet_size_v.append(nbBinsConvolved * self.nbBytePerWaveAmplitude)
                                return_point_waveform_loc_v.append(ptsCenter * timeStep_in_pico_second)
                                x_t_v.append(x_t_pico_second)
                                y_t_v.append(y_t_pico_second)
                                z_t_v.append(z_t_pico_second)

            tmp = dartfile.tell() #saves current position in input file before jump to the data of the next waveform
            tmp += posOffsetPerPulse;

            if ((not feedback==0) and (cnt / feedback) > tmpIndicatorPast):
                tmpIndicatorNew = int(cnt / feedback)
                for i in range(tmpIndicatorPast, tmpIndicatorNew):
                    print('pulse info: %f %f %f' % (pulse_info[6], pulse_info[7], pulse_info[8]))
                    print('elapsed time: {}'.format(time.time()-start))
                    print('{}%'.format(i*10))
                    sys.stdout.flush()
                tmpIndicatorPast=tmpIndicatorNew

                #end of iterative reading the waveform

        print('100%')
        
#         print(points)

##################HEADER#################

        stop = time.time()
        print(stop-start)


        las = laspy.create(file_version=str(self.lasVersion), point_format=self.lasFormat)
        las.header.scales=[self.scale]*3
        las.header.system_identifier='DART5                           '   # length of 32!!!
        las.header.generating_software = 'DART2LAS.py                     '  # length of 32!!!

        digitizer_gain = 1 / receiveWaveGain
        digitizer_offset = 0


        if self.extra_bytes:
            las.add_extra_dims([
                laspy.ExtraBytesParams(name="pulse_width",
                                       description="Full width at half maximum [ns]",
                                       type='f8'),
                laspy.ExtraBytesParams(name="amplitude",
                                       description="Echo signal amplitude [dB]",
                                       type='f8')
            ])
            # description = "RIEGL Extra Bytes."
            # outFile.header.vlrs[0].description = description + "\x00"*(32-len(description))


        if self.ifWriteWaveform:
            # outFile.header.set_waveform_data_packets_external(1)
            # outFile.header.set_waveform_data_packets_internal(
            #     0)  # Equivalent as "outFile.header.set_global_encoding(4)"

            las.header.global_encoding.waveform_data_packets_external = True

            # gencod = bin(outFile.header.get_global_encoding())[2:].zfill(8)
            # print("Global Encoding ", gencod)
            # print("   - Waveform Data Packets Internal ", gencod[-2])
            # print("   - Waveform Data Packets External ", gencod[-3])

            self.digitizer_gain = digitizer_gain
            self.digitizer_offset = digitizer_offset

            # add vlr

            # wvf_str_format = '<BBLLdd'
            # record_data = struct.pack(wvf_str_format, 16, 0, nbBinsConvolved, 1000, digitizer_gain, digitizer_offset)
            # wvf_str = laspy.vlrs.known.WaveformPacketStruct.from_buffer_copy(record_data)
            bits_per_sample = 16
            waveform_compression_type = 0
            number_of_samples = nbBinsConvolved
            temporal_time_spacing = int(timeStep_in_pico_second)  # integer of picosecond
            wvf_str = laspy.vlrs.known.WaveformPacketStruct(bits_per_sample, waveform_compression_type, number_of_samples,
                                                            temporal_time_spacing, digitizer_gain, digitizer_offset)


            # wvf_str.temporal_time_spacing = int(1000)
            # wvf_str.digitizer_gain = 1.0
            # wvf_str.digitizer_offset = 0.0

            wvf_vlr = laspy.vlrs.known.WaveformPacketVlr(100, 'DART waveforms')
            wvf_vlr.parsed_record = wvf_str

            las.vlrs.append(wvf_vlr)
            wave_packet_desc_index_v = [1] * len(x_v)  # select the wavepacket record_id: 1 is record_id-99, here record_id is 100

            #
            #
            # body_fmt = laspy.util.Format(None)
            # body_fmt.add("bits_per_sample", "ctypes.c_ubyte", 1)
            # body_fmt.add("waveform_compression_type", "ctypes.c_ubyte", 1)
            # body_fmt.add("number_of_samples", "ctypes.c_ulong", 1)
            # body_fmt.add("temporal_time_spacing", "ctypes.c_ulong", 1)
            # body_fmt.add("digitizer_gain", "ctypes.c_double", 1)
            # body_fmt.add("digitizer_offset", "ctypes.c_double", 1)
            #
            # print('body_fmt.pt_fmt_long', body_fmt.pt_fmt_long)
            #
            # vlr_body_1 = struct.pack(body_fmt.pt_fmt_long, 16, waveform_compression_type, nbBinsConvolved,
            #                          temporal_time_spacing, digitizer_gain, digitizer_offset)
            # # vlr_body_2 = struct.pack(body_fmt.pt_fmt_long, 8, waveform_compression_type, nbBinsConvolved, temporal_time_spacing, digitizer_gain, digitizer_offset)
            #
            # old_vlrs = outFile.header.vlrs
            # wave_vlr = laspy.vlrs.VLR(user_id='LASF_Spec', record_id=100, record_data=vlr_body_1)
            # # wave_vlr2 = laspy.header.VLR(user_id = 'LASF_Spec', record_id = 101, VLR_body = vlr_body_2)
            # old_vlrs.append(wave_vlr)
            # # old_vlrs.append(wave_vlr2)
            # outFile.header.vlrs = old_vlrs


    ##################POINTS#################
        # remove returns more than maximum (2^3 for formats 1-5)
        if self.lasFormat in range(6, 11):
            Nmax = 2**4-1
        else:
            Nmax = 2**3-1

        num_returns_v = np.array(num_returns_v)
        num_returns_v[num_returns_v>Nmax]=Nmax
        # remove the echoes with return number superior to Nmax
        # this strategy does not ake into account there value, maybe only the greatest intensity echoes
        # should be kept, renumbering them.
        valid_returns = np.array(return_num_v) <= Nmax


        # All formats variables
        if self.lasFormat not in [0, 2]:
            las.gps_time = np.array(gpstime_v)[valid_returns]
        las.x = np.array(x_v)[valid_returns]
        las.y = np.array(y_v)[valid_returns]
        las.z = np.array(z_v)[valid_returns]
        las.intensity = np.array(intensity_v)[valid_returns]
        las.return_number = np.array(return_num_v)[valid_returns]
        las.number_of_returns = np.array(num_returns_v)[valid_returns]

        # Scan angle
        if self.lasFormat in range(6, 11):
            las.scan_angle = np.array(scan_angle_v)[valid_returns]
        else:
            las.scan_angle_rank = np.array(scan_angle_rank_v)[valid_returns]

        # Waveforms
        if self.ifWriteWaveform:
            # [k for k in las.point_format.dimension_names]
            las.wavepacket_index = np.array(wave_packet_desc_index_v)[valid_returns]
            las.wavepacket_offset = np.array(byte_offset_to_waveform_data_v)[valid_returns]
            las.wavepacket_size = np.array(waveform_packet_size_v)[valid_returns]
            las.return_point_wave_location = np.array(return_point_waveform_loc_v)[valid_returns]
            las.x_t = np.array(x_t_v)[valid_returns]
            las.y_t = np.array(y_t_v)[valid_returns]
            las.z_t = np.array(z_t_v)[valid_returns]

        # Extra Bytes
        if self.extra_bytes:
            las.pulse_width=np.array(pulse_width_v)[valid_returns]
            las.amplitude=np.array(amplitude_v)[valid_returns]


        las.write(lasFileName)

        dartfile.close()

        if self.ifWriteWaveform:
            waveformfile.close()


        return digitizer_offset, digitizer_gain
                
    def run(self):
        parser=argparse.ArgumentParser(description='DART2LAS.py script converts a DART LIDAR multi-pulse output file to a LAS File.')

        parser.add_argument('inputFile', type=str, help='input DART LIDAR binary file')
        parser.add_argument('outputFile', type=str, help='output UPD file')
        parser.add_argument('-snf','--solarNoiseFile',type=str, help='set the solar noise input file')
        parser.add_argument('-g','--gain',type=float, help='set a fixed digital gain for the amplitude->volts conversion')
        parser.add_argument('-t','--typeOut',type=int, help='set the output intensity format type (1: Peak amplitude of Gaussian profile; 2: Integration of the decomposed Gaussian profile (Default); 3: Sigma of Gaussian profile (integer value of "sigma(unit: nb of acquisition bins)*10"))')
        parser.add_argument('-w','--waveform',action='store_true', help='set if waveform data is output')


        
        args=parser.parse_args()
        print("args:\n")
        print(args)
        print("####################")

        if args.inputFile:
            print('Input file: '+args.inputFile)

        if args.outputFile:
            print('Output file: '+args.outputFile)
            
        if args.solarNoiseFile:
            print('Solar noise file: '+args.solarNoiseFile)
            self.snFile = args.solarNoiseFile
            self.ifSolarNoise = True
        
        if args.gain:
            self.ifFixedGain = True
            self.fixedGain = args.gain
            print('Digital gain: ',args.gain)
        
        if args.waveform:
            self.ifWriteWaveform = True
            
        
        if args.typeOut:
            if args.typeOut not in [1, 2, 3, 4]:
                print('Error: Unkown option for type of output {}'.format(args.typeOut))
                exit()
            self.typeOut = args.typeOut
            print('Output type: ', args.typeOut)


        self.readDARTBinaryFileAndConvert2LAS(args.inputFile, args.outputFile)

# inputFile=os.path.expanduser('~/DetectedPoints.txt')
# outputFile=os.path.expanduser('~/DetectedPoints.las')
def DP2LAS(inputFile, outputFile, lasFormat = 6):
    """
    Converts DetectedPoints.txt to a LAS file
    Parameters
    ----------
    inputFile: str
        path to DART output file DetectedPoints.txt
    outputFile: str
        path to the LAS file
    lasFormat: int
        Either 1 or 6. LAS Format 1 has a maximum of 7 returns by pulse, while LAS Format 6 has a maximum of 15 returns.
        See LAS 1.4 specifications for details.

    Returns
    -------

    """

    lasVersion = 1.4
    scale = 0.001

    import pandas as pd
    import laspy
    data = pd.read_csv(inputFile, sep='\t', index_col=False)
    extra_col = data.columns[6:]

    ### Write header
    las = laspy.create(file_version=str(lasVersion), point_format=lasFormat)

    las.header.scales = [scale] * 3
    las.header.system_identifier = 'DART5                           '  # length of 32!!!
    las.header.generating_software = 'DART2LAS.py                     '  # length of 32!!!

    # digitizer_gain = 1 / receiveWaveGain
    # digitizer_offset = 0

    extra_byte_params = []
    for c in extra_col:
        extra_byte_params.append(
        laspy.ExtraBytesParams(name=c.lower(),
                               description=c.lower(),
                               data_type=10))

    ### Write data
    if lasFormat in range(6, 11):
        Nmax = 2 ** 4 - 1
    else:
        Nmax = 2 ** 3 - 1

    data.loc[data['NumberReturns'] > Nmax,'NumberReturns'] = Nmax
    # remove the echoes with return number superior to Nmax
    # this strategy does not ake into account there value, maybe only the greatest intensity echoes
    # should be kept, renumbering them.
    data = data.loc[data['ReturnIndx']<=Nmax]

    # All formats variables
    # outFile.set_gps_time(np.array(gpstime_v)[valid_returns])
    las.x = data['X(m)']
    las.y = data['Y(m)']
    las.z = data['Z(m)']
    # outFile.set_intensity(np.array(intensity_v)[valid_returns])
    las.return_number = data['ReturnIndx']
    las.number_of_returns = data['NumberReturns']

    for c in extra_col:
        setattr(las, c.lower(), data[c])

    las.write(outputFile)

if __name__ == '__main__':

    print("hello")

    obj = DART2LAS()
    obj.run()


    print('Done!')
