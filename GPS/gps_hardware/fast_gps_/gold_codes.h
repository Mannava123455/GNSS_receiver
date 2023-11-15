

static void usage(char *message);
void generate_atan2_table(void);
static int count_one_bits(uint_32 *a, int i);
static void g1_lfsr(unsigned char *out);
static void g2_lfsr(unsigned char tap0, unsigned char tap1, unsigned char *out);
static void combine_g1_and_g2(unsigned char *g1, unsigned char *g2, unsigned char *out);
void generateGoldCodes(void);
static void add_to_bitmap(uint_32 *bitmap, int s);
static void bitmap_set_bit(uint_32 *bitmap, int o, int s);
static void stretchGoldCodes(void);
static void mixLocalOscAndGoldCodes(unsigned sample_freq, unsigned if_freq);
int gps_setup(int sample_rate, int if_freq);