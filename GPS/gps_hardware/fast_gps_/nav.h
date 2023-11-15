
static void debug_print_orbit(struct Space_vehicle *sv);
void debug_print_time(struct Space_vehicle *sv);
static unsigned int mask(unsigned u, int n_bits); 
static int sign_extend(unsigned u,int len); 
static unsigned int bits(int val, int offset, int len); 
static unsigned  join_bits_u(int val1, int offset1, int len1, int val2, int offset2, int len2); 
static signed  join_bits_s(int val1, int offset1, int len1, int val2, int offset2, int len2); 
static void nav_save_frame(struct Space_vehicle *sv); 
static int nav_test_telemetry(struct Space_vehicle *sv); 
static const unsigned char parity[32] = 
{
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x13, 0x25,
    0x0B, 0x16, 0x2C, 0x19, 0x32, 0x26, 0x0E, 0x1F,
    0x3E, 0x3D, 0x38, 0x31, 0x23, 0x07, 0x0D, 0x1A,
    0x37, 0x2F, 0x1C, 0x3B, 0x34, 0x2A, 0x16, 0x29};   
static int nav_test_parity(uint_32 d);
static int nav_valid_subframes(struct Space_vehicle *sv);
static void nav_new_bit(struct Space_vehicle *sv, uint_8 s);
static void nav_abandon(struct Space_vehicle *sv); 
static void nav_process(struct Space_vehicle *sv, uint_8 s);
static int nav_read_in_cached_data(struct Space_vehicle *sv); 
static void nav_read_in_all_cached_data(void); 

