#-*-coding: utf8 -*-
'''
Created on Aug 25, 2017

@author: Tiangang Yin
@author: Florian de Boissieu: contribution to format specification and extra bytes integration.
@author: Grégoire Couderc : contribution to format specification.
'''

import re
import sys
import os
import os.path
import struct
import math
import warnings
from datetime import date
import argparse
import laspy
from pprint import pprint
import datetime
import numpy as np
sys.path.append('/home/mpili/mpili/stage/scripts/SmallToLargeFP')
from GaussianDecomposition import *

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
    classdocs
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
        self.prf = 500000.0
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

        if self.lasFormat is None:  # set default format if empty
            if self.ifWriteWaveform:
                self.lasFormat = 4
            else:
                self.lasFormat = 1
        else:  # check format if not empty
            if (self.ifWriteWaveform and (self.lasFormat not in [4, 9])) or (
                    (not self.ifWriteWaveform) and (self.lasFormat not in [1, 6])):
                raise ValueError("LAS format not coherent with ifWriteWaveform:\n"
                                 "ifWriteWaveform must be True for formats 4 and 9,"
                                 "the opposit for formats 1 and 6,\n"
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
                    x_t = -pulse_info[3]
                    y_t = -pulse_info[4]
                    z_t = -pulse_info[5]

                    x0_abs = pulse_info[6] - x_t/2*distToBeginWave #Divided by 2 change from distance to waveform (2 way)
                    y0_abs = pulse_info[7] - y_t/2*distToBeginWave
                    z0_abs = pulse_info[8] - z_t/2*distToBeginWave

                    gpsTime = float(pulse_info[14]) / self.prf

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
                    indexes_peaks = findZeroCrossingPeaks(y_decomp_arr, self.waveNoiseThreshold)

                    ###Gaussian Decomposition
                    if len(indexes_peaks)>0:
                        in_x = np.array(range(len(y_decomp)))+0.5
                        out = gaussian_decomposition(in_x, y_decomp_arr, indexes_peaks)
                        if out.success:
                            # print len(out.best_values)/3, out.best_values['g0_amplitude']
                            if self.ifWriteWaveform:
                                for c in y_decomp:
                                    waveformfile.write(struct.pack('<'+self.waveformAmplitudeFomat,c))
                            countPulses+=1
                            pulsesInBuffer+=1
                            nbPointsDecomp = len(out.best_values)//3

                            for i in range(nbPointsDecomp):
                                ptsPrefix = 'g' + str(i) + '_'
                                ptsAmp = out.best_values[ptsPrefix+'amplitude']
                                ptsSigma = out.best_values[ptsPrefix+'sigma']
                                ptsCenter = out.best_values[ptsPrefix+'center']
        #                         print ptsAmp,   ptsCenter, x0, y0, z0, x_t, y_t, z_t

                                x_abs = x0_abs-x_per_bin*ptsCenter
                                y_abs = y0_abs-y_per_bin*ptsCenter
                                z_abs = z0_abs-z_per_bin*ptsCenter

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
                                x_v.append(int(round( x_abs / self.scale)))
                                y_v.append(int(round( y_abs / self.scale)))
                                z_v.append(int(round( z_abs / self.scale)))
                                intensity_v.append(intensity)
                                if self.lasFormat in range(6, 10):
                                    scan_angle_v.append(scan_angle)
                                else:
                                    scan_angle_rank_v.append(scan_angle_rank)
                                gpstime_v.append(gpsTime)
                                return_num_v.append(i+1)
                                num_returns_v.append(nbPointsDecomp)


                                # Extra Bytes
                                if self.extra_bytes:
                                    pulse_width_v.append(ptsSigma * (2 * math.sqrt(2 * math.log(2)))) # Full Width at Half Maximum
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


        newh=laspy.header.Header(self.lasVersion, self.lasFormat)
        outFile = laspy.file.File(lasFileName, mode="w", header = newh)

        outFile.header.set_scale([self.scale]*3)
        outFile.header.set_systemid('DART5                           ')   # length of 32!!!
        outFile.header.set_softwareid('DART2LAS.py                     ')   # length of 32!!!

        digitizer_gain = 1 / receiveWaveGain
        digitizer_offset = 0

        if self.extra_bytes:
            outFile.define_new_dimension(name="Pulse width",
                                         description="Full width at half maximum [ns]",
                                         data_type=9)
            outFile.define_new_dimension(name="Amplitude",
                                         description="Echo signal amplitude [dB]",
                                         data_type=9)
            outFile.header.vlrs[0].description = "RIEGL Extra Bytes."


        if self.ifWriteWaveform:
            outFile.header.set_waveform_data_packets_external(1)
            outFile.header.set_waveform_data_packets_internal(
                0)  # Equivalent as "outFile.header.set_global_encoding(4)"

            gencod = bin(outFile.header.get_global_encoding())[2:].zfill(8)
            print("Global Encoding ", gencod)
            print("   - Waveform Data Packets Internal ", gencod[-2])
            print("   - Waveform Data Packets External ", gencod[-3])

            # add vlr
            waveform_compression_type = 0
            temporal_time_spacing = int(timeStep_in_pico_second)  # integer of picosecond
            wave_packet_desc_index_v = [1]*len(x_v)  # 1 is record_id-99, here record_id is 100

            self.digitizer_gain = digitizer_gain
            self.digitizer_offset = digitizer_offset

            body_fmt = laspy.util.Format(None)
            body_fmt.add("bits_per_sample", "ctypes.c_ubyte", 1)
            body_fmt.add("waveform_compression_type", "ctypes.c_ubyte", 1)
            body_fmt.add("number_of_samples", "ctypes.c_ulong", 1)
            body_fmt.add("temporal_time_spacing", "ctypes.c_ulong", 1)
            body_fmt.add("digitizer_gain", "ctypes.c_double", 1)
            body_fmt.add("digitizer_offset", "ctypes.c_double", 1)

            print('body_fmt.pt_fmt_long', body_fmt.pt_fmt_long)

            vlr_body_1 = struct.pack(body_fmt.pt_fmt_long, 16, waveform_compression_type, nbBinsConvolved,
                                     temporal_time_spacing, digitizer_gain, digitizer_offset)
            # vlr_body_2 = struct.pack(body_fmt.pt_fmt_long, 8, waveform_compression_type, nbBinsConvolved, temporal_time_spacing, digitizer_gain, digitizer_offset)

            old_vlrs = outFile.header.vlrs
            wave_vlr = laspy.header.VLR(user_id='LASF_Spec', record_id=100, VLR_body=vlr_body_1)
            # wave_vlr2 = laspy.header.VLR(user_id = 'LASF_Spec', record_id = 101, VLR_body = vlr_body_2)
            old_vlrs.append(wave_vlr)
            # old_vlrs.append(wave_vlr2)
            outFile.header.vlrs = old_vlrs


##################POINTS#################

        # All formats variables
        outFile.set_x(x_v)
        outFile.set_y(y_v)
        outFile.set_z(z_v)
        outFile.set_intensity(intensity_v)
        outFile.set_return_num(return_num_v)
        outFile.set_num_returns(num_returns_v)

        # Scan angle
        if self.lasFormat in range(6, 10):
            outFile.set_scan_angle(scan_angle_v)
        else:
            outFile.set_scan_angle_rank(scan_angle_rank_v)

        # Extra Bytes
        if self.extra_bytes:
            outFile.pulse_width=pulse_width_v
            outFile.amplitude=amplitude_v

        # Waveforms
        if self.ifWriteWaveform:
            outFile.set_wave_packet_desc_index(wave_packet_desc_index_v)
            outFile.set_byte_offset_to_waveform_data(byte_offset_to_waveform_data_v)
            outFile.set_waveform_packet_size(waveform_packet_size_v)
            outFile.set_return_point_waveform_loc(return_point_waveform_loc_v)
            outFile.set_x_t(x_t_v)
            outFile.set_y_t(y_t_v)
            outFile.set_z_t(z_t_v)


        outFile.close() 
                       
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

if __name__ == '__main__':

    print("hello")

    obj = DART2LAS()
    obj.run()


    print('Done!')
