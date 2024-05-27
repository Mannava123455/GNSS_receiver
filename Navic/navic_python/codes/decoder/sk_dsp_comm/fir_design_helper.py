"""
Basic Linear Phase Digital Filter Design Helper

Copyright (c) March 2017, Mark Wickert
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
"""

import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from logging import getLogger
log = getLogger(__name__)


def firwin_lpf(n_taps, fc, fs = 1.0):
    """
    Design a windowed FIR lowpass filter in terms of passband
    critical frequencies f1 < f2 in Hz relative to sampling rate
    fs in Hz. The number of taps must be provided.
    
    Mark Wickert October 2016
    """
    return signal.firwin(n_taps, 2 * fc / fs)


def firwin_bpf(n_taps, f1, f2, fs = 1.0, pass_zero=False):
    """
    Design a windowed FIR bandpass filter in terms of passband
    critical frequencies f1 < f2 in Hz relative to sampling rate
    fs in Hz. The number of taps must be provided.

    Mark Wickert October 2016
    """
    return signal.firwin(n_taps, 2 * (f1, f2) / fs, pass_zero=pass_zero)


def firwin_kaiser_lpf(f_pass, f_stop, d_stop, fs = 1.0, n_bump=0, status = True):
    """
    Design an FIR lowpass filter using the sinc() kernel and
    a Kaiser window. The filter order is determined based on 
    f_pass Hz, f_stop Hz, and the desired stopband attenuation
    d_stop in dB, all relative to a sampling rate of fs Hz.
    Note: the passband ripple cannot be set independent of the
    stopband attenuation.

    Mark Wickert October 2016
    """
    wc = 2*np.pi*(f_pass + f_stop)/2/fs
    delta_w = 2*np.pi*(f_stop - f_pass)/fs
    # Find the filter order
    M = np.ceil((d_stop - 8)/(2.285*delta_w))
    # Adjust filter order up or down as needed
    M += n_bump
    N_taps = M + 1
    # Obtain the Kaiser window
    beta = signal.kaiser_beta(d_stop)
    w_k = signal.kaiser(N_taps,beta)
    n = np.arange(N_taps)
    b_k = wc/np.pi*np.sinc(wc/np.pi*(n-M/2)) * w_k
    b_k /= np.sum(b_k)
    if status:
        log.info('Kaiser Win filter taps = %d.' % N_taps)
    return b_k


def firwin_kaiser_hpf(f_stop, f_pass, d_stop, fs = 1.0, n_bump=0, status = True):
    """
    Design an FIR highpass filter using the sinc() kernel and
    a Kaiser window. The filter order is determined based on 
    f_pass Hz, f_stop Hz, and the desired stopband attenuation
    d_stop in dB, all relative to a sampling rate of fs Hz.
    Note: the passband ripple cannot be set independent of the
    stopband attenuation.

    Mark Wickert October 2016
    """
    # Transform HPF critical frequencies to lowpass equivalent
    f_pass_eq = fs/2. - f_pass
    f_stop_eq = fs/2. - f_stop
    # Design LPF equivalent
    wc = 2*np.pi*(f_pass_eq + f_stop_eq)/2/fs
    delta_w = 2*np.pi*(f_stop_eq - f_pass_eq)/fs
    # Find the filter order
    M = np.ceil((d_stop - 8)/(2.285*delta_w))
    # Adjust filter order up or down as needed
    M += n_bump
    N_taps = M + 1
    # Obtain the Kaiser window
    beta = signal.kaiser_beta(d_stop)
    w_k = signal.kaiser(N_taps,beta)
    n = np.arange(N_taps)
    b_k = wc/np.pi*np.sinc(wc/np.pi*(n-M/2)) * w_k
    b_k /= np.sum(b_k)
    # Transform LPF equivalent to HPF
    n = np.arange(len(b_k))
    b_k *= (-1)**n
    if status:
        log.info('Kaiser Win filter taps = %d.' % N_taps)
    return b_k


def firwin_kaiser_bpf(f_stop1, f_pass1, f_pass2, f_stop2, d_stop,
                      fs = 1.0, n_bump=0, status = True):
    """
    Design an FIR bandpass filter using the sinc() kernel and
    a Kaiser window. The filter order is determined based on 
    f_stop1 Hz, f_pass1 Hz, f_pass2 Hz, f_stop2 Hz, and the 
    desired stopband attenuation d_stop in dB for both stopbands,
    all relative to a sampling rate of fs Hz.
    Note: the passband ripple cannot be set independent of the
    stopband attenuation.

    Mark Wickert October 2016    
    """
    # Design BPF starting from simple LPF equivalent
    # The upper and lower stopbands are assumed to have 
    # the same attenuation level. The LPF equivalent critical
    # frequencies:
    f_pass = (f_pass2 - f_pass1)/2
    f_stop = (f_stop2 - f_stop1)/2
    # Continue to design equivalent LPF
    wc = 2*np.pi*(f_pass + f_stop)/2/fs
    delta_w = 2*np.pi*(f_stop - f_pass)/fs
    # Find the filter order
    M = np.ceil((d_stop - 8)/(2.285*delta_w))
    # Adjust filter order up or down as needed
    M += n_bump
    N_taps = M + 1
    # Obtain the Kaiser window
    beta = signal.kaiser_beta(d_stop)
    w_k = signal.kaiser(N_taps,beta)
    n = np.arange(N_taps)
    b_k = wc/np.pi*np.sinc(wc/np.pi*(n-M/2)) * w_k
    b_k /= np.sum(b_k)
    # Transform LPF to BPF
    f0 = (f_pass2 + f_pass1)/2
    w0 = 2*np.pi*f0/fs
    n = np.arange(len(b_k))
    b_k_bp = 2*b_k*np.cos(w0*(n-M/2))
    if status:
        log.info('Kaiser Win filter taps = %d.' % N_taps)
    return b_k_bp


def firwin_kaiser_bsf(f_stop1, f_pass1, f_pass2, f_stop2, d_stop,
                      fs = 1.0, n_bump=0, status = True):
    """
    Design an FIR bandstop filter using the sinc() kernel and
    a Kaiser window. The filter order is determined based on 
    f_stop1 Hz, f_pass1 Hz, f_pass2 Hz, f_stop2 Hz, and the 
    desired stopband attenuation d_stop in dB for both stopbands,
    all relative to a sampling rate of fs Hz.
    Note: The passband ripple cannot be set independent of the
    stopband attenuation.
    Note: The filter order is forced to be even (odd number of taps)
    so there is a center tap that can be used to form 1 - H_BPF.

    Mark Wickert October 2016    
    """
    # First design a BPF starting from simple LPF equivalent
    # The upper and lower stopbands are assumed to have 
    # the same attenuation level. The LPF equivalent critical
    # frequencies:
    f_pass = (f_pass2 - f_pass1)/2
    f_stop = (f_stop2 - f_stop1)/2
    # Continue to design equivalent LPF
    wc = 2*np.pi*(f_pass + f_stop)/2/fs
    delta_w = 2*np.pi*(f_stop - f_pass)/fs
    # Find the filter order
    M = np.ceil((d_stop - 8)/(2.285*delta_w))
    # Adjust filter order up or down as needed
    M += n_bump
    # Make filter order even (odd number of taps)
    if ((M+1)/2.0-int((M+1)/2.0)) == 0:
        M += 1
    N_taps = M + 1
    # Obtain the Kaiser window
    beta = signal.kaiser_beta(d_stop)
    w_k = signal.kaiser(N_taps,beta)
    n = np.arange(N_taps)
    b_k = wc/np.pi*np.sinc(wc/np.pi*(n-M/2)) * w_k
    b_k /= np.sum(b_k)
    # Transform LPF to BPF
    f0 = (f_pass2 + f_pass1)/2
    w0 = 2*np.pi*f0/fs
    n = np.arange(len(b_k))
    b_k_bs = 2*b_k*np.cos(w0*(n-M/2))
    # Transform BPF to BSF via 1 - BPF for odd N_taps
    b_k_bs = -b_k_bs
    b_k_bs[int(M/2)] += 1
    if status:
        log.info('Kaiser Win filter taps = %d.' % N_taps)
    return b_k_bs


def lowpass_order(f_pass, f_stop, dpass_dB, dstop_dB, fsamp = 1):
    """
    Optimal FIR (equal ripple) Lowpass Order Determination
    
    Text reference: Ifeachor, Digital Signal Processing a Practical Approach, 
    second edition, Prentice Hall, 2002.
    Journal paper reference: Herriman et al., Practical Design Rules for Optimum
    Finite Imulse Response Digitl Filters, Bell Syst. Tech. J., vol 52, pp. 
    769-799, July-Aug., 1973.IEEE, 1973.
    """
    dpass = 1 - 10**(-dpass_dB/20)
    dstop = 10**(-dstop_dB/20)
    Df = (f_stop - f_pass)/fsamp
    a1 = 5.309e-3
    a2 = 7.114e-2
    a3 = -4.761e-1
    a4 = -2.66e-3
    a5 = -5.941e-1
    a6 = -4.278e-1
    
    Dinf = np.log10(dstop)*(a1*np.log10(dpass)**2 + a2*np.log10(dpass) + a3) \
           + (a4*np.log10(dpass)**2 + a5*np.log10(dpass) + a6)
    f = 11.01217 + 0.51244*(np.log10(dpass) - np.log10(dstop))
    N = Dinf/Df - f*Df + 1
    ff = 2*np.array([0, f_pass, f_stop, fsamp/2])/fsamp
    aa = np.array([1, 1, 0, 0])
    wts = np.array([1.0, dpass/dstop])
    return int(N), ff, aa, wts


def bandpass_order(f_stop1, f_pass1, f_pass2, f_stop2, dpass_dB, dstop_dB, fsamp = 1):
    """
    Optimal FIR (equal ripple) Bandpass Order Determination
    
    Text reference: Ifeachor, Digital Signal Processing a Practical Approach, 
    second edition, Prentice Hall, 2002.
    Journal paper reference: F. Mintzer & B. Liu, Practical Design Rules for Optimum
    FIR Bandpass Digital Filters, IEEE Transactions on Acoustics and Speech, pp. 
    204-206, April,1979.
    """
    dpass = 1 - 10**(-dpass_dB/20)
    dstop = 10**(-dstop_dB/20)
    Df1 = (f_pass1 - f_stop1)/fsamp
    Df2 = (f_stop2 - f_pass2)/fsamp
    b1 = 0.01201
    b2 = 0.09664
    b3 = -0.51325
    b4 = 0.00203
    b5 = -0.5705
    b6 = -0.44314
    
    Df = min(Df1, Df2)
    Cinf = np.log10(dstop)*(b1*np.log10(dpass)**2 + b2*np.log10(dpass) + b3) \
           + (b4*np.log10(dpass)**2 + b5*np.log10(dpass) + b6)
    g = -14.6*np.log10(dpass/dstop) - 16.9
    N = Cinf/Df + g*Df + 1
    ff = 2*np.array([0, f_stop1, f_pass1, f_pass2, f_stop2, fsamp/2])/fsamp
    aa = np.array([0, 0, 1, 1, 0, 0])
    wts = np.array([dpass/dstop, 1, dpass/dstop])
    return int(N), ff, aa, wts


def bandstop_order(f_stop1, f_pass1, f_pass2, f_stop2, dpass_dB, dstop_dB, fsamp = 1):
    """
    Optimal FIR (equal ripple) Bandstop Order Determination
    
    Text reference: Ifeachor, Digital Signal Processing a Practical Approach, 
    second edition, Prentice Hall, 2002.
    Journal paper reference: F. Mintzer & B. Liu, Practical Design Rules for Optimum
    FIR Bandpass Digital Filters, IEEE Transactions on Acoustics and Speech, pp. 
    204-206, April,1979.
    """
    dpass = 1 - 10**(-dpass_dB/20)
    dstop = 10**(-dstop_dB/20)
    Df1 = (f_pass1 - f_stop1)/fsamp
    Df2 = (f_stop2 - f_pass2)/fsamp
    b1 = 0.01201
    b2 = 0.09664
    b3 = -0.51325
    b4 = 0.00203
    b5 = -0.5705
    b6 = -0.44314
    
    Df = min(Df1, Df2)
    Cinf = np.log10(dstop)*(b1*np.log10(dpass)**2 + b2*np.log10(dpass) + b3) \
           + (b4*np.log10(dpass)**2 + b5*np.log10(dpass) + b6)
    g = -14.6*np.log10(dpass/dstop) - 16.9
    N = Cinf/Df + g*Df + 1
    ff = 2*np.array([0, f_stop1, f_pass1, f_pass2, f_stop2, fsamp/2])/fsamp
    aa = np.array([1, 1, 0, 0, 1, 1])
    wts = np.array([2, dpass/dstop, 2])
    return int(N), ff, aa, wts


def fir_remez_lpf(f_pass, f_stop, d_pass, d_stop, fs = 1.0, n_bump=5, status = True):
    """
    Design an FIR lowpass filter using remez with order
    determination. The filter order is determined based on 
    f_pass Hz, fstop Hz, and the desired passband ripple 
    d_pass dB and stopband attenuation d_stop dB all 
    relative to a sampling rate of fs Hz.

    Mark Wickert October 2016, updated October 2018
    """
    n, ff, aa, wts = lowpass_order(f_pass, f_stop, d_pass, d_stop, fsamp=fs)
    # Bump up the order by N_bump to bring down the final d_pass & d_stop
    N_taps = n
    N_taps += n_bump
    b = signal.remez(N_taps, ff, aa[0::2], wts,Hz=2)
    if status:
        log.info('Remez filter taps = %d.' % N_taps)
    return b


def fir_remez_hpf(f_stop, f_pass, d_pass, d_stop, fs = 1.0, n_bump=5, status = True):
    """
    Design an FIR highpass filter using remez with order
    determination. The filter order is determined based on 
    f_pass Hz, fstop Hz, and the desired passband ripple 
    d_pass dB and stopband attenuation d_stop dB all 
    relative to a sampling rate of fs Hz.

    Mark Wickert October 2016, updated October 2018
    """
    # Transform HPF critical frequencies to lowpass equivalent
    f_pass_eq = fs/2. - f_pass
    f_stop_eq = fs/2. - f_stop
    # Design LPF equivalent
    n, ff, aa, wts = lowpass_order(f_pass_eq, f_stop_eq, d_pass, d_stop, fsamp=fs)
    # Bump up the order by N_bump to bring down the final d_pass & d_stop
    N_taps = n
    N_taps += n_bump
    b = signal.remez(N_taps, ff, aa[0::2], wts,Hz=2)
    # Transform LPF equivalent to HPF
    n = np.arange(len(b))
    b *= (-1)**n
    if status:
        log.info('Remez filter taps = %d.' % N_taps)
    return b


def fir_remez_bpf(f_stop1, f_pass1, f_pass2, f_stop2, d_pass, d_stop,
                  fs = 1.0, n_bump=5, status = True):
    """
    Design an FIR bandpass filter using remez with order
    determination. The filter order is determined based on 
    f_stop1 Hz, f_pass1 Hz, f_pass2 Hz, f_stop2 Hz, and the 
    desired passband ripple d_pass dB and stopband attenuation
    d_stop dB all relative to a sampling rate of fs Hz.

    Mark Wickert October 2016, updated October 2018
    """
    n, ff, aa, wts = bandpass_order(f_stop1, f_pass1, f_pass2, f_stop2, 
                                  d_pass, d_stop, fsamp=fs)
    # Bump up the order by N_bump to bring down the final d_pass & d_stop
    N_taps = n
    N_taps += n_bump
    b = signal.remez(N_taps, ff, aa[0::2], wts,Hz=2)
    if status:
        log.info('Remez filter taps = %d.' % N_taps)
    return b


def fir_remez_bsf(f_pass1, f_stop1, f_stop2, f_pass2, d_pass, d_stop,
                  fs = 1.0, n_bump=5, status = True):
    """
    Design an FIR bandstop filter using remez with order
    determination. The filter order is determined based on 
    f_pass1 Hz, f_stop1 Hz, f_stop2 Hz, f_pass2 Hz, and the 
    desired passband ripple d_pass dB and stopband attenuation
    d_stop dB all relative to a sampling rate of fs Hz.

    Mark Wickert October 2016, updated October 2018
    """
    n, ff, aa, wts = bandstop_order(f_pass1, f_stop1, f_stop2, f_pass2, 
                                    d_pass, d_stop, fsamp=fs)
    # Bump up the order by N_bump to bring down the final d_pass & d_stop
    # Initially make sure the number of taps is even so N_bump needs to be odd
    if np.mod(n,2) != 0:
        n += 1
    N_taps = n
    N_taps += n_bump
    b = signal.remez(N_taps, ff, aa[0::2], wts, Hz=2,
                     maxiter = 25, grid_density = 16)
    if status:
        log.info('N_bump must be odd to maintain odd filter length')
        log.info('Remez filter taps = %d.' % N_taps)
    return b


def freqz_resp_list(b, a=np.array([1]), mode = 'dB', fs=1.0, n_pts = 1024, fsize=(6, 4)):
    """
    A method for displaying digital filter frequency response magnitude,
    phase, and group delay. A plot is produced using matplotlib

    freq_resp(self,mode = 'dB',Npts = 1024)

    A method for displaying the filter frequency response magnitude,
    phase, and group delay. A plot is produced using matplotlib

    freqz_resp(b,a=[1],mode = 'dB',Npts = 1024,fsize=(6,4))

        b = ndarray of numerator coefficients
        a = ndarray of denominator coefficents
     mode = display mode: 'dB' magnitude, 'phase' in radians, or 
            'groupdelay_s' in samples and 'groupdelay_t' in sec, 
            all versus frequency in Hz
     Npts = number of points to plot; default is 1024
    fsize = figure size; defult is (6,4) inches

    Mark Wickert, January 2015
    """
    if type(b) == list:
        # We have a list of filters
        N_filt = len(b)
    f = np.arange(0, n_pts) / (2.0 * n_pts)
    for n in range(N_filt):
        w,H = signal.freqz(b[n],a[n],2*np.pi*f)
        if n == 0:
            plt.figure(figsize=fsize)
        if mode.lower() == 'db':
            plt.plot(f*fs,20*np.log10(np.abs(H)))
            if n == N_filt-1:
                plt.xlabel('Frequency (Hz)')
                plt.ylabel('Gain (dB)')
                plt.title('Frequency Response - Magnitude')

        elif mode.lower() == 'phase':
            plt.plot(f*fs,np.angle(H))
            if n == N_filt-1:
                plt.xlabel('Frequency (Hz)')
                plt.ylabel('Phase (rad)')
                plt.title('Frequency Response - Phase')

        elif (mode.lower() == 'groupdelay_s') or (mode.lower() == 'groupdelay_t'):
            """
            Notes
            -----

            Since this calculation involves finding the derivative of the
            phase response, care must be taken at phase wrapping points 
            and when the phase jumps by +/-pi, which occurs when the 
            amplitude response changes sign. Since the amplitude response
            is zero when the sign changes, the jumps do not alter the group 
            delay results.
            """
            theta = np.unwrap(np.angle(H))
            # Since theta for an FIR filter is likely to have many pi phase
            # jumps too, we unwrap a second time 2*theta and divide by 2
            theta2 = np.unwrap(2*theta)/2.
            theta_dif = np.diff(theta2)
            f_diff = np.diff(f)
            Tg = -np.diff(theta2)/np.diff(w)
            # For gain almost zero set groupdelay = 0
            idx = np.nonzero(np.ravel(20*np.log10(H[:-1]) < -400))[0]
            Tg[idx] = np.zeros(len(idx))
            max_Tg = np.max(Tg)
            #print(max_Tg)
            if mode.lower() == 'groupdelay_t':
                max_Tg /= fs
                plt.plot(f[:-1]*fs,Tg/fs)
                plt.ylim([0,1.2*max_Tg])
            else:
                plt.plot(f[:-1]*fs,Tg)
                plt.ylim([0,1.2*max_Tg])
            if n == N_filt-1:
                plt.xlabel('Frequency (Hz)')
                if mode.lower() == 'groupdelay_t':
                    plt.ylabel('Group Delay (s)')
                else:
                    plt.ylabel('Group Delay (samples)')
                plt.title('Frequency Response - Group Delay')
        else:
            s1 = 'Error, mode must be "dB", "phase, '
            s2 = '"groupdelay_s", or "groupdelay_t"'
            log.info(s1 + s2)
