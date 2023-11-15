

static void snapshot_timing(struct Snapshot *s);
static double  orbit_ecc_anom(struct Space_vehicle *sv, double t);
static void sv_calc_corrected_time(int i);
static int orbit_calc_position(struct Space_vehicle *sv, struct Location *l);
static int sv_calc_location(int id, struct Location *l);
int A_solve(int chans, struct Location *sv_l, struct Location *p);
static void LatLonAlt(double x_n, double y_n, double z_n,double *lat, double *lon, double *alt);
static void attempt_solution(struct Snapshot *s);