cmake_minimum_required(VERSION 3.16)

set(PROJECT_BASE_NAME generic-chimeratk-server)
# Unfortunately application core does not allow hyphens in the app name. Have to use underscore.
set(CHIMERATK_APP_NAME generic_chimeratk_server)

if(ADAPTER STREQUAL "OPCUA")
  set(PROJECT_NAME_PREFIX opcua-)
elseif(ADAPTER STREQUAL "DOOCS")
  set(PROJECT_NAME_PREFIX doocs-)
elseif(ADAPTER STREQUAL "EPICSIOC")
  set(PROJECT_NAME_PREFIX epics-)
elseif(ADAPTER STREQUAL "EPICS7IOC")
  set(PROJECT_NAME_PREFIX epics7-)
endif()

set(${PROJECT_BASE_NAME}_MAJOR_VERSION 01)
set(${PROJECT_BASE_NAME}_MINOR_VERSION 03)
set(${PROJECT_BASE_NAME}_PATCH_VERSION 00)
include(${CMAKE_SOURCE_DIR}/cmake/set_version_numbers.cmake)

project(${PROJECT_NAME_PREFIX}${PROJECT_BASE_NAME}${${PROJECT_BASE_NAME}_MAJOR_VERSION})

list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/Modules)

# Set the build type to Release if none is specified
# Force it into Release if "None" is specified (needed to overrule dkpg_buildpackage)
if(NOT CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL "None")
  set(CMAKE_BUILD_TYPE "Release" CACHE STRING
      "Choose the type of build, options are: Debug Release RelWithDebInfo MinSizeRel."
      FORCE)
endif(NOT CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL "None")

include(cmake/set_default_flags.cmake)

set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

include(cmake/enable_code_coverage_report.cmake)
include(cmake/set_control_system_adapter.cmake)
find_package(ChimeraTK-ApplicationCore 03.00 REQUIRED)
find_package(ChimeraTK-DeviceAccess-DoocsBackend 01.04 REQUIRED)

aux_source_directory(${CMAKE_SOURCE_DIR}/server server_sources)
aux_source_directory(${CMAKE_SOURCE_DIR}/src library_sources)

set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

include_directories(${CMAKE_SOURCE_DIR}/include)

# library for code shared between server executable and tests
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

add_library(${PROJECT_NAME}_impl STATIC ${library_sources} )
target_link_libraries(${PROJECT_NAME}_impl ChimeraTK::ChimeraTK-ApplicationCore)

# main server executable
add_executable(${PROJECT_NAME} ${server_sources})
target_link_libraries(${PROJECT_NAME} PUBLIC ${PROJECT_NAME}_impl
                      PRIVATE ChimeraTK::SelectedAdapter)

add_executable(${PROJECT_NAME}-xmlGenerator ${server_sources})
target_compile_options(${PROJECT_NAME}-xmlGenerator PRIVATE "-DGENERATE_XML")
target_link_libraries(${PROJECT_NAME}-xmlGenerator PUBLIC ${PROJECT_NAME}_impl)

# copy example configuration to build directory - this is also needed for the tests
# The doocs server config and doocs adapter config
FILE( COPY sample_configs/ DESTINATION ${PROJECT_BINARY_DIR})
