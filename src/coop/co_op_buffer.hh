#ifndef __COOP_BUFFER_HH__
#define __COOP_BUFFER_HH__

#include "params/CoOpBuffer.hh"
#include "sim/sim_object.hh"

class CoOpBuffer : public SimObject
{
    public:
        int pkt_arr[10];
        int owner_arr[10];

        int size;
        int filled;

        //constructor
        CoOpBuffer(CoOpBufferParams *p);

        int get_size();
        int get_pkt(int pos);
};
#endif // __COOP_BUFFER_HH__
