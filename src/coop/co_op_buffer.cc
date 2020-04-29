#include "coop/co_op_buffer.hh"
#include "debug/Coop.hh"

CoOpBuffer::CoOpBuffer(CoOpBufferParams *params) :
    SimObject(params)
{
   
    int i;
    size = 10;
    filled = 10;

    for(i = 0; i < size; i++)
    {
        pkt_arr[i] = 90 + i;
        owner_arr[i] = i %4;
    }
    
    DPRINTF(Coop, "Created the coop object !!!!!!!!!!!!!!!!!!!!!!!! \n");
}

int 
CoOpBuffer::get_size()
{
    return size;
}

int
CoOpBuffer::get_pkt(int pos)
{
    if(pos < size)
    {
        return pkt_arr[pos];
    }
    return -1;
}

CoOpBuffer*
CoOpBufferParams::create()
{
    return new CoOpBuffer(this);
}