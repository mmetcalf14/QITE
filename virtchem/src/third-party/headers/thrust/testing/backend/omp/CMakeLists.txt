set(DRIVER_BACKEND "")
FILE(GLOB SOURCES_CU  *.cu)
FILE(GLOB SOURCES_CPP *.cpp)

set(SOURCES_BACKEND ${SOURCES_BACKEND} ${SOURCES_CU} ${SOURCES_CPP} PARENT_SCOPE)
set(DRIVER ${DRIVER} ${DRIVER_BACKEND} PARENT_SCOPE)
