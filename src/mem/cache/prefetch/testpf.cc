
#include "mem/cache/prefetch/testpf.hh"

#include <cassert>

#include "base/intmath.hh"
#include "base/logging.hh"
#include "base/random.hh"
#include "base/trace.hh"
#include "debug/HWPrefetch.hh"
#include "mem/cache/replacement_policies/base.hh"
#include "params/TestPF.hh"
#include <utility>

#define IML_SIZE 8192
#define PREFETCH_DEGREE 16
#define TEMPORAL_SIZE 256


std::deque <Addr> gl_iml[4];
uint gl_num_pf = 0;


TestPF::TestPF(const TestPFParams *p)
    : QueuedPrefetcher(p),
      degree(p->degree)
{
    pf_id = gl_num_pf ++;
    printf("TESTPF !!!! Creating TestPF prefetcher %d ..........................\n", pf_id);
}


void
TestPF::notifyRetiredInst(const Addr pc)
{
    // if(iml.size() < IML_SIZE) {
    //     if(iml.size() == 0) {
    //         iml.push_back(pc);
    //     }   
    //     else if(iml.back() != pc){
    //         iml.push_back(pc);
    //     }
    //     return;
    // }
    // else{
    //     if(iml.back() != pc){
    //         iml.pop_front();
    //         iml.push_back(pc);
    //     }
    // }
    
}


void
TestPF::calculatePrefetch(const PrefetchInfo &pfi,
                                    std::vector<AddrPriority> &addresses)
{
    // if (!pfi.hasPC()) {
    //     DPRINTF(HWPrefetch, " TESTPF !!!! Ignoring request with no PC.\n");
    //     return;
    // }

    int found = 0;

    // Get required packet info
    Addr pf_addr = pfi.getAddr();
    // Addr pc = pfi.getPC();

    if(gl_iml[pf_id].size() < IML_SIZE) {
        if(gl_iml[pf_id].size() == 0) {
            gl_iml[pf_id].push_back(pf_addr);
        }   
        else if(gl_iml[pf_id].back() != pf_addr){
            gl_iml[pf_id].push_back(pf_addr);
        }
        return;
    }
    else{
        if(gl_iml[pf_id].back() != pf_addr){
            gl_iml[pf_id].pop_front();
            gl_iml[pf_id].push_back(pf_addr);
        }
    }

    //DPRINTF(HWPrefetch, "TESTPF !!!! Calc Pref called : PC %x pkt_addr %x \n", pc, pf_addr);
    
    // check in own queue first 
    for(int i = gl_iml[pf_id].size() - degree - 1; i > 0; i--) {
        if(pf_addr == gl_iml[pf_id][i]) {
            for(int k = 1; k <= degree; k++) {
                DPRINTF(HWPrefetch, "Prefetching! from own queue %x \n", gl_iml[pf_id][i+k]);
                addresses.push_back(AddrPriority(gl_iml[pf_id][i+k], 0));
                found = 1;
            }
            break;
        }
    }

    if(!found)
    {
        //check in other queues
        for(int pf_id_it = 0; pf_id_it < gl_num_pf; pf_id_it++)
        {
            if(pf_id_it == pf_id)
                continue;

            for(int i = gl_iml[pf_id_it].size() - degree - 1; i > 0; i--) {
                if(pf_addr == gl_iml[pf_id_it][i]) {
                    for(int k = 1; k <= degree; k++) {
                        DPRINTF(HWPrefetch, "Prefetching! from other %x \n", gl_iml[pf_id_it][i+k]);
                        addresses.push_back(AddrPriority(gl_iml[pf_id_it][i+k], 0));
                    }
                    break;
                }
            }
        }
    }


    // for (int d = 1; d <= degree; d++) {
    //     Addr new_addr = pf_addr + d * blkSize;
    //     DPRINTF(HWPrefetch, "TESTPF !!!! Calling pushback : pkt_addr %x \n", new_addr);

    //     addresses.push_back(AddrPriority(new_addr, 0));
    // }
}

TestPF*
TestPFParams::create()
{
    return new TestPF(this);
}

TestPF::~TestPF()
{
    printf("Calling destructor ...... !!!!!!");
}

void
TestPF::PrefetchListenerPC::notify(const Addr& pc)
{
    parent.notifyRetiredInst(pc);
}

void
TestPF::addEventProbeRetiredInsts(SimObject *obj, const char *name)
{
    ProbeManager *pm(obj->getProbeManager());
    listenersPC.push_back(new PrefetchListenerPC(*this, pm, name));
}
