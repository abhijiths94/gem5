
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

TestPF::TestPF(const TestPFParams *p)
    : QueuedPrefetcher(p),
      degree(p->degree)
{
    printf("TESTPF !!!! Creating TestPF prefetcher ..........................\n");
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


    // Get required packet info
    Addr pf_addr = pfi.getAddr();
    // Addr pc = pfi.getPC();

    if(iml.size() < IML_SIZE) {
        if(iml.size() == 0) {
            iml.push_back(pf_addr);
        }   
        else if(iml.back() != pf_addr){
            iml.push_back(pf_addr);
        }
        return;
    }
    else{
        if(iml.back() != pf_addr){
            iml.pop_front();
            iml.push_back(pf_addr);
        }
    }

    //DPRINTF(HWPrefetch, "TESTPF !!!! Calc Pref called : PC %x pkt_addr %x \n", pc, pf_addr);

    for(int i = iml.size() - PREFETCH_DEGREE - 1; i > 0; i--) {
        if(pf_addr == iml[i]) {
            for(int k = 1; k <= PREFETCH_DEGREE; k++) {
                DPRINTF(HWPrefetch, "Prefetching! %x \n", iml[i+k]);
                addresses.push_back(AddrPriority(iml[i+k], 0));
            }
            break;
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