cmake_minimum_required(VERSION 3.16)

project(ChimeraTK-Generic-Device-Server)

set(EXE_BASE_NAME generic-chimeratk-server)
# Unfortunately application core does not allow hyphens in the app name. Have to use underscore.
set(CHIMERATK_APP_NAME generic_chimeratk_server)

if(ADAPTER STREQUAL "OPCUA")
  set(EXE_NAME_PREFIX opcua-)
elseif(ADAPTER STREQUAL "DOOCS")
  set(EXE_NAME_PREFIX doocs-)
elseif(ADAPTER STREQUAL "EPICSIOC")
  set(EXE_NAME_PREFIX epics-)
elseif(ADAPTER STREQUAL "EPICS7IOC")
  set(EXE_NAME_PREFIX epics7-)
elseif(ADAPTER STREQUAL "TANGO")
  set(EXE_NAME_PREFIX tango-)
endif()

set(${PROJECT_NAME}_MAJOR_VERSION 02)
set(${PROJECT_NAME}_MINOR_VERSION 00)
set(${PROJECT_NAME}_PATCH_VERSION 01)
include(${CMAKE_SOURCE_DIR}/cmake/set_version_numbers.cmake)

set(EXE_NAME ${EXE_NAME_PREFIX}${EXE_BASE_NAME}${${PROJECT_NAME}_MAJOR_VERSION})

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

aux_source_directory(${CMAKE_SOURCE_DIR}/server server_sources)
aux_source_directory(${CMAKE_SOURCE_DIR}/src library_sources)

set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

include_directories(${CMAKE_SOURCE_DIR}/include)

# library for code shared between server executable and tests
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

add_library(${EXE_NAME}_impl ${library_sources})
target_link_libraries(${EXE_NAME}_impl ChimeraTK::ChimeraTK-ApplicationCore)

# main server executable
add_executable(${EXE_NAME} ${server_sources})
target_link_libraries(${EXE_NAME} PUBLIC ${EXE_NAME}_impl PRIVATE ChimeraTK::SelectedAdapter)

add_executable(${EXE_NAME}-xmlGenerator ${server_sources})
target_compile_options(${EXE_NAME}-xmlGenerator PRIVATE "-DGENERATE_XML")
target_link_libraries(${EXE_NAME}-xmlGenerator PUBLIC ${EXE_NAME}_impl)

# The application configuration and map/dmap files
file(GLOB CONIG_FILES ${CMAKE_SOURCE_DIR}/sample_configs/*)
file(COPY ${CONFIG_FILES} DESTINATION ${PROJECT_BINARY_DIR})

find_package(Boost COMPONENTS unit_test_framework)

# Test executables and helper scripts
foreach(target writeWordStatus testGenericServer)
    add_executable(${target} tests/${target}.cc)
    target_link_libraries(${target} PUBLIC ${EXE_NAME}_impl PRIVATE Boost::unit_test_framework)
endforeach()

enable_testing()
#don't add the helper scripts as tests
add_test(testGenericServer ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/testGenericServer)

#install executables
install(TARGETS ${EXE_NAME} RUNTIME DESTINATION bin)
