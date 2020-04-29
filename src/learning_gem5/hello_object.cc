#include "learning_gem5/hello_object.hh"
#include <iostream>
#include "debug/Hello.hh"

HelloObject::HelloObject(HelloObjectParams *params) :
    SimObject(params)
{
    DPRINTF(Hello, "Created the hello object\n");

}

HelloObject*
HelloObjectParams::create()
{
    return new HelloObject(this);
}
