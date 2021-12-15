FetchContent_Declare(
  cbc
  URL https://www.coin-or.org/download/source/Cbc/Cbc-2.10.5.tgz
  URL_HASH MD5=46277180c0fc67f750e2de1836333189
)
include(ProcessorCount)
ProcessorCount(N)
if (N GREATER 8)
  set (N 8)
endif ()
message(STATUS "Building CBC library from source.")
FetchContent_GetProperties(cbc)
if(NOT cbc_POPULATED)
  FetchContent_Populate(cbc)
  include(ExternalProject)
  message(STATUS "Cbc src in ${cbc_SOURCE_DIR} ${cbc_BINARY_DIR}")
  message(STATUS ${MAKE})
  message(STATUS ${cbc_PREFIX_DIR})
  ExternalProject_Add(cbc
      SOURCE_DIR ${cbc_SOURCE_DIR}
      CONFIGURE_COMMAND ${cbc_SOURCE_DIR}/configure --enable-openmp --disable-zlib --disable-bzlib --without-blas --without-lapack --enable-static --disable-shared --with-pic --prefix=${cbc_BINARY_DIR}
      BUILD_BYPRODUCTS ${cbc_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}Cbc${CMAKE_STATIC_LIBRARY_SUFFIX}
      BUILD_COMMAND make -j${N}
      BUILD_IN_SOURCE 1
      )
  ExternalProject_Add(Cgl
      SOURCE_DIR ${cbc_SOURCE_DIR}/Cgl
      CONFIGURE_COMMAND ""
      BUILD_COMMAND ""
      INSTALL_COMMAND ""
      BUILD_BYPRODUCTS ${cbc_BINARY_DIR}/lib/libCgl.a
      BUILD_IN_SOURCE 1
      )
  set(cbc_LIBRARIES
    ${cbc_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}Cbc${CMAKE_STATIC_LIBRARY_SUFFIX}
    ${cbc_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}Cgl${CMAKE_STATIC_LIBRARY_SUFFIX}
    ${cbc_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}Clp${CMAKE_STATIC_LIBRARY_SUFFIX}
    ${cbc_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}Osi${CMAKE_STATIC_LIBRARY_SUFFIX}
    ${cbc_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}OsiCbc${CMAKE_STATIC_LIBRARY_SUFFIX}
    ${cbc_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}OsiClp${CMAKE_STATIC_LIBRARY_SUFFIX}
    ${cbc_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}CoinUtils${CMAKE_STATIC_LIBRARY_SUFFIX}
    )
  
  ExternalProject_Add(Clp
      SOURCE_DIR ${cbc_SOURCE_DIR}/Clp
      CONFIGURE_COMMAND ""
      BUILD_COMMAND ""
      INSTALL_COMMAND ""
      BUILD_BYPRODUCTS ${cbc_BINARY_DIR}/lib/libClp.a
      )
  ExternalProject_Add(CoinUtils
      SOURCE_DIR ${cbc_SOURCE_DIR}/CoinUtils
      CONFIGURE_COMMAND ""
      BUILD_COMMAND ""
      INSTALL_COMMAND ""
      BUILD_BYPRODUCTS ${cbc_BINARY_DIR}/lib/libCoinUtils.a
      )
  ExternalProject_Add(Osi
      SOURCE_DIR ${cbc_SOURCE_DIR}/Osi
      CONFIGURE_COMMAND ""
      BUILD_COMMAND ""
      INSTALL_COMMAND ""
      BUILD_BYPRODUCTS ${cbc_BINARY_DIR}/lib/libOsi.a
      )
  ExternalProject_Add(OsiCbc
      SOURCE_DIR ${cbc_SOURCE_DIR}/Cbc/src/OsiCbc
      CONFIGURE_COMMAND ""
      BUILD_COMMAND ""
      INSTALL_COMMAND ""
      BUILD_BYPRODUCTS ${cbc_BINARY_DIR}/lib/libOsiCbc.a
      )
  ExternalProject_Add(OsiClp
      SOURCE_DIR ${cbc_SOURCE_DIR}/Clp/src/OsiClp
      CONFIGURE_COMMAND ""
      BUILD_COMMAND ""
      INSTALL_COMMAND ""
      BUILD_BYPRODUCTS ${cbc_BINARY_DIR}/lib/libOsiClp.a
      )
endif()
