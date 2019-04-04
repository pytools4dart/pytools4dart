#coding: utf-8

import lmfit
import numpy as np
import matplotlib.pyplot as plt
import pprint

def findZeroCrossingPeaks(y, intThreshold=5, min_dist=3):
    '''Detecte Zero Crossing Peaks'''
    peak_list = []
    if len(y)>0:
        waveformLengthLess1 = len(y) - 1
        gradients = []
        for i in range(waveformLengthLess1):
            gradients.append(y[i+1]-y[i])
#         firstPeak = True
#         peakInt = 0
#         peakTime = 0
#         timeDiff = 0
#         calcThreshold = .0
        
        for i in range(waveformLengthLess1-1):
            for j in range(i+1,waveformLengthLess1):
                if gradients[i] == 0:
                    break
                if (not gradients[j] == 0) and gradients[i]>0 and gradients[j]<0:
#                     print j, gradients[i], gradients[j]
                    if y[i+1]>intThreshold:
                        peak_list.append(i+1)
                    break
                elif (not gradients[j] == 0):
                    break
    peaks = np.array(peak_list)
    if peaks.size > 1 and min_dist > 1:
        highest = peaks[np.argsort(y[peaks])][::-1]
        rem = np.ones(y.size, dtype=bool)
        rem[peaks] = False

        for peak in highest:
            if not rem[peak]:
                sl = slice(max(0, peak - min_dist), peak + min_dist + 1)
                rem[sl] = True
                rem[peak] = False

        peaks = np.arange(y.size)[~rem]
        print(peaks)
    return peaks


#Old approach from Jianbo
def detect_peaks(y, thres=0.3, min_dist=3):
    '''Peak detection routine.

            Finds the peaks in *y* by taking its first order difference. By using
            *thres* and *min_dist* parameters, it is possible to reduce the number of
            detected peaks.

            Parameters
            ----------
            y : ndarray
                1D amplitude data to search for peaks.
            thres : float between [0., 1.]
                Normalized threshold. Only the peaks with amplitude higher than the
                threshold will be detected.
            min_dist : int
                Minimum distance between each detected peak. The peak with the highest
                amplitude is preferred to satisfy this constraint.

            Returns
            -------
            ndarray
                Array containing the indexes of the peaks that were detected
            '''
    thres *= np.max(y) - np.min(y)

    # find the peaks by using the first order difference
    dy = np.diff(y)
    peaks = np.where((np.hstack([dy, 0.]) < 0.)
                     & (np.hstack([0., dy]) > 0.)
                     & (y > thres))[0]


    if peaks.size > 1 and min_dist > 1:
        highest = peaks[np.argsort(y[peaks])][::-1]
        rem = np.ones(y.size, dtype=bool)
        rem[peaks] = False

        for peak in highest:
            if not rem[peak]:
                sl = slice(max(0, peak - min_dist), peak + min_dist + 1)
                rem[sl] = True
                rem[peak] = False

        peaks = np.arange(y.size)[~rem]

    return peaks


def remove_duplicate(y):
    for i in range(1, len(y)):
        if y[i] == y[i-1]:
            y[i] += 0.001*y[i]
    return y


def find_inflexion(y, indexes):
    if len(indexes) > 1:
        intervals = []
        for index in indexes:
            # left
            li = index
            while li > 0 and y[li-1] <= y[li]:
                li -= 1
            # right
            ri = index
            while ri < len(y) - 1 and y[ri+1] <= y[ri]:
                ri += 1
            interval = [li, ri]
            intervals.append(interval)
        return intervals
    else:
        return [[0, len(y)-1]]


def gaussian_decomposition(x, y, indexes_peaks):
#     y = remove_duplicate(y)
    # find the peaks
#     detect_peaks(y, thres=0.2, min_dist=5)
    inter = find_inflexion(y, indexes_peaks)
#     print 'inter', inter
    # number of gaussian components
    pars = None
    mod = None
    for i in range(0, len(indexes_peaks)):
        model_prefix = 'g' + str(i) + '_'
        gauss_component = lmfit.models.GaussianModel(prefix=model_prefix)

#         print 'par', y[inter[i][0]:inter[i][1] + 1], x[inter[i][0]:inter[i][1] + 1]
        if pars is None:
            # pars = gauss_component.make_params()
            pars = gauss_component.guess(y[inter[i][0]:inter[i][1] + 1], x=x[inter[i][0]:inter[i][1] + 1])
        else:
            pars.update(gauss_component.guess(y[inter[i][0]:inter[i][1] + 1], x=x[inter[i][0]:inter[i][1] + 1]))
        pars['%ssigma' % model_prefix].set(min=0.0)
        pars['%sfwhm' % model_prefix].set(min=0.0)
        pars['%scenter' % model_prefix].set(min=0.0)
        pars['%samplitude' % model_prefix].set(min=0.0)

        if mod is None:
            mod = gauss_component
        else:
            mod += gauss_component
    out = mod.fit(y, pars, x=x)
    return out

if __name__ == '__main__':

    data = np.loadtxt(open(r"/home/ctpp/WORK/GaussianDecomposition/text.txt", "rb"), delimiter=";", skiprows=1)
    #data = np.loadtxt(r'E:\Research\23-DART-DAO\FullWaveform\model1d_gauss.txt')
    
    
    intThresholdArg = False
    intWaveNoiseThreshold = 0 # Threshold to consider as noise
    
    decay = 5
    decayThres = 100
    
    window = 5
    noiseSet = False
    allPulse = True
    
    
    x = data[:, 0]
    y = data[:, 1]
    
    indexes_peaks = findZeroCrossingPeaks(y, 5)
    if not len(indexes_peaks)==0:
        out = gaussian_decomposition(x, y, indexes_peaks)
        # print out.fit_report()
        pprint.pprint(out.__dict__);
        print(out.success)
        print(len(out.best_values))
        print(out.best_values['g0_sigma'])
         
        plt.plot(x, out.best_fit, 'r-', label="Fitting")
         
        # dy = np.diff(y)
        # plt.plot(x, np.hstack([dy, 0.]), '-', label='First order difference')
         
        plt.plot([0, 700], [0, 0], 'k-')
         
        plt.plot(x, y, '.', label='LiDAR waveform')
        # plt.scatter(x[indexes], y[indexes], marker="o", facecolors='r', edgecolors='r', s=50, label='Detected peaks')
        # plt.legend(loc='upper center')
         
        plt.show()
