function [peak_ind, peak_power, peak_to_noise_ratio , peak_ind_interpolated , peak_to_noise_ratio_interpolated ] = Search_correlation_peak( corr_in, SPS )
%
% SPS - is the number of samples per chip. It is used for interpolation of correlation peak
%


en_debug = 0;
en_paek_interpolation = 0;

Len = length(corr_in);
corr_in_abs = abs(corr_in);


% find maximum
[peak_power,peak_ind] = max(corr_in_abs);


% check if more that one max was found, then take the first one
if length(peak_power) > 1peak_to_noise_ratio = corr_in_abs(peak_ind) / noise;
    warning('Search_correlation_peak.m : More than one maximum was found. Taking the 1st one and ignoring others!');
    peak_power = peak_power(1);
    peak_ind = peak_ind(1);
end


% measure peak to noise ratio
peak_indexes = mod(((peak_ind-2):(peak_ind+2))-1,Len)+1;
other_indexes = setdiff(1:Len,peak_indexes);


if en_paek_interpolation

    if peak_ind == Len
        late_ind = 1;
    else
        late_ind = peak_ind +1;
    end

    if peak_ind == 1
        early_ind = Len;
    else
        early_ind = peak_ind - 1;
    end


    y_late = corr_in_abs(late_ind);
    y_early = corr_in_abs(early_ind);
    y_prompt = corr_in_abs(peak_ind);


    % Interpolate to find peak power
    if (y_late > y_early)
        x1 = peak_ind;
        y1 = y_prompt;
        x2 = late_ind;
        y2 = y_late;    
    else
        x1 = early_ind;
        y1 = y_early;
        x2 = peak_ind;
        y2 = y_prompt;
    end


    % Interpolate to find peak index
    % Note: this code works only 2x samples per chip (or close to it)
    % TODO: 
    r = y1/y2;
    % Make sure that 0.5<r<2
    if r<0.5
        r=0.5;
        warning('Search correlation peak: wrong input values!');
    elseif r>2
        r=2;
        warning('Search correlation peak: wrong input values!');
    end
    X1 = (1/2*r-1) / (1+r);
    X2 = 0.5 + X1;


    peak_ind_interpolated = x1 - X1*2;
    % peak_ind_interpolated = x2 - X2*2;

    peak_power_interpolated = y1/(1+X1);
    % peak_power_interpolated = y2/(1-X2);
    
    % ----------------------------------------------------
    % Old interploation code
    % peak_power_interpolated = (x1*y2 + x2*y1) / (x1+x2);
    % r = y_late/y_early;
    % d = 1/SPS;
    % x = (1-r) * (1-d) / (1+r);
    % peak_ind_interpolated = peak_ind - x * SPS;
    % ----------------------------------------------------
    
else
    peak_ind_interpolated = peak_ind;
    peak_power_interpolated = peak_power;
end
    
    





noise =  mean(corr_in_abs(other_indexes));
peak_to_noise_ratio = corr_in_abs(peak_ind) / noise;
peak_to_noise_ratio_interpolated = peak_power_interpolated / noise;



if en_debug
    M = peak_power_interpolated;
    
    figure
    x_low = linspace(-1,0,100);
    y_low = M*(1+x_low);
    
    x_high = linspace(0,1,100);
    y_high = M*(1-x_high);
    
    plot([x_low,x_high],[y_low,y_high]);
    hold on
    plot([X1-0.5,X1,X2,X2+0.5],[corr_in_abs(x1-1),y1,y2,corr_in_abs(x2+1)],'rx');
    
    
    
end

end

