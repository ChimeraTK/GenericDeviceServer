cmake_minimum_required(VERSION 3.16)

set(PROJECT_BASE_NAME generic-chimeratk)
set(CHIMERATK_APP_NAME generic_chimeratk_server)

if(ADAPTER STREQUAL "OPCUA")
  set(PROJECT_NAME_PREFIX opcua-)
elseif(ADAPTER STREQUAL "DOOCS")
  set(PROJECT_NAME_PREFIX doocs-)
elseif(ADAPTER STREQUAL "EPICSIOC")
  set(PROJECT_NAME_PREFIX epics-)
endif()

set(${PROJECT_NAME}_MAJOR_VERSION 01)
set(${PROJECT_NAME}_MINOR_VERSION 00)
set(${PROJECT_NAME}_PATCH_VERSION 00)
include(${CMAKE_SOURCE_DIR}/cmake/set_version_numbers.cmake)

project(${PROJECT_NAME_PREFIX}${PROJECT_BASE_NAME}_server${${PROJECT_NAME}_MAJOR_VERSION})

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

include(${CMAKE_SOURCE_DIR}/cmake/add_dependency.cmake)
include(cmake/enable_code_coverage_report.cmake)
include(cmake/set_control_system_adapter.cmake)
add_dependency(ChimeraTK-ApplicationCore 02.02 REQUIRED)
add_dependency(ChimeraTK-DeviceAccess-DoocsBackend REQUIRED)

#FIND_PACKAGE(Boost COMPONENTS unit_test_framework REQUIRED)

list(GET ChimeraTK-DeviceAccess-DoocsBackend_LIBRARIES 0 DoocsBackendLibSymlink)
get_filename_component(DoocsBackendLib ${DoocsBackendLibSymlink} REALPATH)
message(${DoocsBackendLib})

aux_source_directory(${CMAKE_SOURCE_DIR}/server server_sources)

set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
#INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/include headers)

#configure_file(include/version.h.in ${PROJECT_BINARY_DIR}/version.h)
include_directories(${PROJECT_BINARY_DIR})

# library for code shared between server executable and tests
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

# main server executable
add_executable(${PROJECT_NAME} ${server_sources})
set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_FLAGS "${ChimeraTK-ApplicationCore_CXX_FLAGS}")
set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "${ChimeraTK-ApplicationCore_LINK_FLAGS} ${Adapter_LINK_FLAGS}")
target_link_libraries(${PROJECT_NAME} ${ChimeraTK-ApplicationCore_LIBRARIES}
                      ${Adapter_LIBRARIES}
                      ${ChimeraTK-DeviceAccess-DoocsBackend_LIBRARIES})

add_executable(${PROJECT_NAME}-xmlGenerator ${server_sources})
set_target_properties(${PROJECT_NAME}-xmlGenerator PROPERTIES COMPILE_FLAGS "-DGENERATE_XML")
set_target_properties(${PROJECT_NAME}-xmlGenerator PROPERTIES LINK_FLAGS "${ChimeraTK-ApplicationCore_LINK_FLAGS} ${Adapter_LINK_FLAGS}")
target_link_libraries(${PROJECT_NAME}-xmlGenerator ${ChimeraTK-ApplicationCore_LIBRARIES}
                      ${ChimeraTK-DeviceAccess-DoocsBackend_LIBRARIES})


# copy example configuration to build directory - this is also needed for the tests
#file(COPY ${CMAKE_SOURCE_DIR}/sample_configs/RPC_LIBNO DESTINATION ${PROJECT_BINARY_DIR})
FILE(COPY ${CMAKE_SOURCE_DIR}/sample_configs/${PROJECT_BASE_NAME}-server01.conf DESTINATION ${PROJECT_BINARY_DIR})
FILE(COPY ${CMAKE_SOURCE_DIR}/sample_configs/${PROJECT_BASE_NAME}-server-DoocsVariableConfig.xml DESTINATION ${PROJECT_BINARY_DIR})
FILE(COPY ${CMAKE_SOURCE_DIR}/sample_configs/${PROJECT_BASE_NAME}-server_configuration.xml DESTINATION ${PROJECT_BINARY_DIR})
file(COPY ${CMAKE_SOURCE_DIR}/sample_configs/devices.dmap DESTINATION ${PROJECT_BINARY_DIR})
file(COPY ${CMAKE_SOURCE_DIR}/sample_configs/rfsync_mo13synth_flmo_0.0.0-75-g063b93e1.mapp DESTINATION ${PROJECT_BINARY_DIR})
file(COPY ${CMAKE_SOURCE_DIR}/sample_configs/initscript.sh DESTINATION ${PROJECT_BINARY_DIR})


install(TARGETS ${PROJECT_NAME}
  RUNTIME DESTINATION bin
)
