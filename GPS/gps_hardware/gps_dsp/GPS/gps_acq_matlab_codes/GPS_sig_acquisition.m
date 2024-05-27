function Params = GPS_sig_acquisition(Sig_DFE,Params)
%
%
%



en_plot = Params.Acquisition.en_plot;
en_print = Params.Acquisition.en_print;

% Params.Acquisition.delay_in_chips = 10.0;
% Params.Acquisition.fft_size = 2048;
% Params.Acquisition.satellites_to_search = [1];


SPS = Params.SPS_DFE_output;
N_satellites_for_search = numel(Params.Acquisition.satellites_to_search); 
N_dopplers_for_search = numel(Params.Acquisition.dopplers_to_search); 
N_offsets_for_search = numel(Params.Acquisition.TO_to_search);
N_fft = Params.Acquisition.fft_size;
N_coherent_periods = Params.Acquisition.N_coherent_acquisition_periods;
N_non_coherent_periods = Params.Acquisition.N_non_coherent_acquisition_periods;
i_SNR = Params.i_SNR;

f_sam = SPS * 1.023e6; % in Hz

Frame_size = round(1023*Params.SPS_DFE_output);


N0_est = (var(real(Sig_DFE)) + var(imag(Sig_DFE)))/2;
sigma_n_est = sqrt(N0_est);


if en_print
    fprintf('-------------------------------  Starting Acquisition  -------------------------------\n');
    fprintf('Searching the sky:\n');
end

% Init acquisition results struct
N_SNR = length(Params.scenario.SNR_vec);
for i=1:N_SNR,
    Params.Acquisition.res.Max_corr_val{i_SNR} = zeros(1,32);
    Params.Acquisition.res.Time_offset{i_SNR} = zeros(1,32);
    Params.Acquisition.res.Doppler_est{i_SNR} = zeros(1,32);
    Params.Acquisition.res.Peak_relative_power{i_SNR} = zeros(1,32);
end


% --------------------------------------------------
% Search per satellite
% --------------------------------------------------
for i_sat = 1:N_satellites_for_search,
    
    % ----------------------------------------------------------------
    % Generate C/A code with SPS=1 
    %    and then resample it to SPS and cyclically extend to N_fft
    % ----------------------------------------------------------------
    n_sat = Params.Acquisition.satellites_to_search(i_sat);  % Satellite number
    CA_sig_SPS1 = 2*cacode(n_sat,1)-1;
    
    
    % Comment - CA cade is re-generated for each ackuisition period
    %CA_sig = cacode_resample(CA_sig_SPS1,SPS,N_fft);
    %CA_sig_fft = fft(CA_sig);
    
    Params.Acquisition.res.Max_corr_val{i_SNR}(n_sat) = 0;
    
    X_corr_res = zeros(N_fft,N_dopplers_for_search);
    
    
    % ----------------------------------------------------------------
    % Search for fractional TO
    % ----------------------------------------------------------------
    for i_TO = 1:N_offsets_for_search,
    
        TO = Params.Acquisition.TO_to_search(i_TO);
    
        % ----------------------------------------------------------------
        % Search for Dopper hypothesis
        % ----------------------------------------------------------------
        for i_doppler = 1:N_dopplers_for_search,
            % Generate doppler freq offset
            f_doppler = Params.Acquisition.dopplers_to_search(i_doppler); % in Hz

            doppler_demod_vec = exp( -1j*2*pi*f_doppler/f_sam * (0:(length(Sig_DFE)-1)) );
            Sig_DFE_doppler = Sig_DFE .* doppler_demod_vec; 

            Sig_non_coherent_product = zeros(1,N_fft);


            CA_code_phase = 0; % reset CA code phase
            start_ind = round(1+ Params.SPS_DFE_output * Params.Acquisition.delay_in_chips);
            end_ind = start_ind + Params.Acquisition.fft_size - 1;
            for i_non_coherent_period=1:N_non_coherent_periods,
                % ----------------------------------------------------------------
                % Coherent integration
                % ----------------------------------------------------------------
                Sig_coherent_product = zeros(1,N_fft);

                for i_coherent_period=1:N_coherent_periods,

                    if end_ind > length(Sig_DFE)
                        %fprintf(1,'Too short sample. Stopping after %d periods!\n',i_non_coherent_period-1);
                        break
                    end

                    % Generate CA sig
                    CA_code_phase_vec = CA_code_phase + TO + (0:(N_fft-1)) / SPS;
                    CA_code_phase_next_sample = CA_code_phase_vec(end) + 1/SPS;
                    CA_code_phase = CA_code_phase_next_sample - 1023; % Update phase for the next epoch
                    CA_code_phase_vec = floor(CA_code_phase_vec);
                    CA_code_phase_vec = mod(CA_code_phase_vec,1023);
                    CA_sig = CA_sig_SPS1(CA_code_phase_vec+1); % +1 since Matlab vector idex starts from 1
                    CA_sig_fft = fft(CA_sig);

                    % Cyclic correlation in frequency domain
                    Sig_one_symbol = Sig_DFE_doppler(start_ind:end_ind);
                    Sig_one_symbol_fft =  conj( fft(Sig_one_symbol) );
                    Sig_coherent_product = Sig_coherent_product + Sig_one_symbol_fft .* CA_sig_fft;

                    start_ind = start_ind + Frame_size;
                    end_ind = end_ind + Frame_size;
                end


                % ----------------------------------------------------------------
                % Non Coherent integration
                % ----------------------------------------------------------------
                Sig_circ_corr = ifft(Sig_coherent_product);
                Sig_non_coherent_product = Sig_non_coherent_product + abs(Sig_circ_corr);



                if end_ind > length(Sig_DFE)
                    break;
                end

            end

            % ----------------------------------------------------------------
            % Find correlation peak
            % ----------------------------------------------------------------   
            [coh_peak_ind, coh_peak_power, coh_peak_to_noise_ratio, coh_peak_ind_int, coh_peak_to_noise_ratio_int ] = Search_correlation_peak( Sig_circ_corr, SPS );
            [non_coh_peak_ind, non_coh_peak_power, non_coh_peak_to_noise_ratio, non_coh_peak_ind_int, non_coh_peak_to_noise_ratio_int ] = Search_correlation_peak( Sig_non_coherent_product, SPS );
            if 0 %en_print
                fprintf(1,'non coherent period = %d\n',i_non_coherent_period);
                fprintf(1,'Coherent: peak ind = %d (%.2f), peak_pwer=%.2f peak_to_noise=%.2f (%.2f)\n',coh_peak_ind,coh_peak_ind_int,coh_peak_power,coh_peak_to_noise_ratio,coh_peak_to_noise_ratio_int);
                fprintf(1,'Non-Coherent: peak ind = %d (%.2f), peak_pwer=%.2f peak_to_noise=%.2f (%.2f)\n',non_coh_peak_ind,non_coh_peak_ind_int,non_coh_peak_power,non_coh_peak_to_noise_ratio,non_coh_peak_to_noise_ratio_int);
            end

            [max_corr,max_ind] = max(Sig_non_coherent_product);

            if max_corr > Params.Acquisition.res.Max_corr_val{i_SNR}(n_sat)
                %Params.Acquisition.res.Time_offset{i_SNR}(n_sat) = non_coh_peak_ind_int - 1;
                Params.Acquisition.res.Time_offset{i_SNR}(n_sat) = max_ind - 1 + TO;
                Params.Acquisition.res.Max_corr_val{i_SNR}(n_sat) = max_corr;
                Params.Acquisition.res.Doppler_est{i_SNR}(n_sat) = f_doppler;
                Params.Acquisition.res.Peak_relative_power{i_SNR}(n_sat) = non_coh_peak_to_noise_ratio_int;
                Params.Acquisition.res.Xcorr_res{n_sat} = Sig_non_coherent_product;
            end




            X_corr_res(:,i_doppler) = Sig_circ_corr(:);



        
        end
        
    end
    
    if en_plot
        %for i_sat=1:32
        %figure(i_sat);
        figure;
        plot(Params.Acquisition.res.Xcorr_res{n_sat});
        grid on
        hold on
        ##title(['SV=',num2str(Params.Acquisition.satellites_to_search(i_sat)) ,...
          ##  '    Peak rel power=',num2str(round(Params.Acquisition.res.Peak_relative_power{i_SNR}(n_sat),2))]);
        ##axis tight
    end
    
    
    
    
    
    % ----------------------------------------------------------------
    % Display report of what was found
    % ----------------------------------------------------------------
    if en_print
        %Peak_val = Params.Acquisition.res.Max_corr_val{i_SNR}(n_sat)/sigma_n_est/1023/Params.Acquisition.N_coherent_acquisition_periods;
        Doppler_val =  round(Params.Acquisition.res.Doppler_est{i_SNR}(n_sat)); % in Hz
        CA_offset_val = Params.Acquisition.res.Time_offset{i_SNR}(n_sat);
        
        Peak_rel_val = Params.Acquisition.res.Peak_relative_power{i_SNR}(n_sat);
        
        if Peak_rel_val > Params.Acquisition.Xcorr_th
            fprintf('\t\t\tSat %d: Doppler=%dHz, C/A offset=%.2f Peak_relative_power=%.2f  <--- Found\n',...
                Params.Acquisition.satellites_to_search(i_sat),...
                Doppler_val,...
                CA_offset_val,...
                Params.Acquisition.res.Peak_relative_power{i_SNR}(n_sat)...
                );
        else
            fprintf('\t\t\tSat %d: Doppler=%dHz, C/A offset=%.2f Peak_relative_power=%.2f\n',...
                Params.Acquisition.satellites_to_search(i_sat),...
                Doppler_val,...
                CA_offset_val,...
                Params.Acquisition.res.Peak_relative_power{i_SNR}(n_sat)...
                );
        end
        fprintf('------------------------------------------------------------------------------------\n');
    end
    
    
end

fprintf('-------------------------------  Finished Acquisition  -------------------------------\n');


end

