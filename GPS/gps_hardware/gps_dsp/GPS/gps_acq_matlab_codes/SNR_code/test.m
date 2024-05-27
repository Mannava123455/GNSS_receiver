file = "gpssim.bin";
fiq = fopen(file, "rb");  % "rb" stands for read binary

if fiq == -1
    error("Could not open the file %s", file);
end

% Read binary data into a vector of int8
c = fread(fiq, Inf, 'int8');

fclose(fiq);
data_in_hex = complex(c(1:2:end),c(2:2:end));
L_res = mod(length(data_in_hex),Frame_size_ceil);
data_in_hex = data_in_hex(1:end-L_res);

data_in_hex_r = reshape(data_in_hex,2048,[]);
data_in_hex_r = data_in_hex_r(1:2048,:);
data_in_hex = data_in_hex_r(:);
data_in =data_in_hex(1:end);
