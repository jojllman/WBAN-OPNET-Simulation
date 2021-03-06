/* Include files */
// Distribution Modeling sub-package
#include <oms_dist_support.h>
#include "headers\wban_math.h"
#include "headers\wban_params.h"
#include "headers\wban_struct.h"

/* Node configuration constants		*/

/* Special attribute values			*/
#define	SC_INFINITE_TIME		-1.0

/* Interrupt code values			*/
#define	SC_START			0
#define	SC_STOP				1

#define	SC_GENERATE_UP0		10
#define	SC_GENERATE_UP1		11
#define	SC_GENERATE_UP2		12
#define	SC_GENERATE_UP3		13
#define	SC_GENERATE_UP4		14
#define	SC_GENERATE_UP5		15
#define	SC_GENERATE_UP6		16
#define	SC_GENERATE_UP7		17

/* Input and output streams		*/
#define	STRM_FROM_UP_TO_MAC	0

/* State machine conditions 		*/
#define	START					((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_START))
#define	DISABLED				((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_STOP))
#define	STOP					((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_STOP))

#define	UP0_MSDU_GENERATE		((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_GENERATE_UP0))
#define	UP1_MSDU_GENERATE		((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_GENERATE_UP1))
#define	UP2_MSDU_GENERATE		((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_GENERATE_UP2))
#define	UP3_MSDU_GENERATE		((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_GENERATE_UP3))
#define	UP4_MSDU_GENERATE		((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_GENERATE_UP4))
#define	UP5_MSDU_GENERATE		((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_GENERATE_UP5))
#define	UP6_MSDU_GENERATE		((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_GENERATE_UP6))
#define	UP7_MSDU_GENERATE		((op_intrpt_type () == OPC_INTRPT_SELF) && (op_intrpt_code () == SC_GENERATE_UP7))

/* Function prototypes.				*/
static void wban_source_init (void);
static void wban_print_parameters (void);
static void wban_up0_traffic_generate (void);
static void wban_up1_traffic_generate (void);
static void wban_up2_traffic_generate (void);
static void wban_up3_traffic_generate (void);
static void wban_up4_traffic_generate (void);
static void wban_up5_traffic_generate (void);
static void wban_up6_traffic_generate (void);
static void wban_up7_traffic_generate (void);

/* Global variables.				*/
extern int app_sent_msdu_nbr; // Number of MSDU generated by the Application Layer
extern double app_sent_msdu_bits; // MSDUs sent by the Application Layer [kbits]
