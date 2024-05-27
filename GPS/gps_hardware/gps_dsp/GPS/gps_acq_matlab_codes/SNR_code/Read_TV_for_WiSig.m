clear all
% close all
% clc

dbstop if error

% Configurations
%hex_filename = 'Out_TV_FLT_16MHz.hex'; % <--Set file path here
Frame_size = 2048; % !!! <- Important: In your case you should set 2040. In currrent example we use different rate here.

Params.Acquisition.en_plot = 0; % <- enable/disable plot option
Params.Acquisition.en_print = 0; % <- debug prints should be enabled
Params.Acquisition.satellites_to_search =  1:32; % <- Specify a vector of satellites to serarch in range 1 to 32
Params.Acquisition.dopplers_to_search = -25000:500:25000; % <- Specify Doppler search range

%%

if Frame_size == 2048
    Frame_size_ceil = 2048;
elseif Frame_size == 4080
    Frame_size_ceil = 4096;
end



% Specify the file name
file_name = 'i.dat';
file_name1 = 'q.dat';
% Load data from the file
data_I = load(file_name);
data_Q = load(file_name1);


data_in_hex = complex(data_I,data_Q);
L_res = mod(length(data_in_hex),Frame_size_ceil);
data_in_hex = data_in_hex(1:end-L_res);

data_in_hex_r = reshape(data_in_hex,Frame_size_ceil,[]);
data_in_hex_r = data_in_hex_r(1:Frame_size,:);
data_in_hex = data_in_hex_r(:);
data_in =data_in_hex(1:20480);














Params.SPS_DFE_output = 2 * Frame_size/2046;


Params.Acquisition.fft_size = Frame_size;
Params.Acquisition.N_coherent_acquisition_periods = 2;
Params.Acquisition.N_non_coherent_acquisition_periods = 1;
Params.Acquisition.delay_in_chips = 1; % not important
Params.Acquisition.Xcorr_th = 6;
Params.i_SNR = 1;
Params.Acquisition.TO_to_search = 0;
Params.scenario.SNR_vec = 0;


reference_visible_satellites = [18,24,23,15,10]
reference_doppler_frequency_average = -14400;

for snr = -22 :-21
        noise_signal = awgn(data_in,snr);
        error = 0;
        for iter = 1:1000
                Params = GPS_sig_acquisition(noise_signal.',Params);
                for i = 1:32
                  p(i) =   Params.Acquisition.res.Peak_relative_power{1}(i);
                endfor
              
              
                for i = 1:32
                  doppler(i) = Params.Acquisition.res.Doppler_est{1}(i);
                endfor
              
                power = sort(p);
                [power, indices] = sort(p);
              
                visible_satellites = indices(28:32);
                top_5_visible_satellites = fliplr(visible_satellites);
              
                for index = 1:length(top_5_visible_satellites)
                   value = top_5_visible_satellites (index);
                   doppler_freq_for_visible_satellites(index) = doppler(value);
                  
                endfor
                
                average = mean(doppler_freq_for_visible_satellites);
                
                if ~isequal(top_5_visible_satellites, reference_visible_satellites)
                  if average != reference_doppler_frequency_average
                    error = error + 1;
                  endif
                endif
                disp(error);
        endfor
        probability_of_error(snr) = error/1000;
        disp(probability_of_error(snr));

endfor



##
##  disp(top_5_visible_satellites);
##  disp('');
##  disp(doppler_freq_for_visible_satellites)
##  disp('');

disp('');
disp(probability_of_error);


