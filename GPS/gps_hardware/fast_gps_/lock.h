
#include "nav.h"


static void start_locked(struct Space_vehicle *sv, int offset_from_peak); 
static void accumulate(struct Space_vehicle *sv, int sample); 
static void update_early(struct Space_vehicle *sv, int prompt_code_index, int prompt_code_index_next_cycle);
static void adjust_prompt(struct Space_vehicle *sv); 
static void update_prompt(struct Space_vehicle *sv, int prompt_code_index, int prompt_code_index_next_cycle); 
static void update_late(struct Space_vehicle *sv, int prompt_code_index, int prompt_code_index_next_cycle);
static void adjust_early_late(struct Space_vehicle *sv) ;
static void update_ncos(struct Space_vehicle *sv) ;