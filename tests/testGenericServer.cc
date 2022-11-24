// SPDX-FileCopyrightText: Deutsches Elektronen-Synchrotron DESY, MSK, ChimeraTK Project <chimeratk-support@desy.de>
// SPDX-License-Identifier: LGPL-3.0-or-later

#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE GenericServerTest
#include <boost/test/unit_test.hpp>
using namespace boost::unit_test_framework;

#include "GenericApp.h"

#include <ChimeraTK/ApplicationCore/TestFacility.h>
namespace ctk = ChimeraTK;

struct GenericServerFixture {
  GenericApp testApp;
  ctk::TestFacility test{testApp};

  GenericServerFixture() { test.runApplication(); }
};

BOOST_FIXTURE_TEST_CASE(testDevicesAreThere, GenericServerFixture) {
  // both devices are there and functional
  BOOST_TEST(test.getScalar<int32_t>("/Devices/TMCB1/status") == 1);
  BOOST_TEST(test.getScalar<int32_t>("/Devices/TMCB2/status") == 1);
}

BOOST_FIXTURE_TEST_CASE(testPathInDevice, GenericServerFixture) {
  // TMCB1 directly maps BSP, while TMBC2 does not have an entry for pathInDevice and maps all FW modules

  BOOST_CHECK_NO_THROW(test.getScalar<uint32_t>("TMCB1/WORD_ID"));
  BOOST_CHECK_NO_THROW(test.getScalar<uint32_t>("TMCB2/BSP/WORD_ID"));
}

BOOST_FIXTURE_TEST_CASE(testIntiScript, GenericServerFixture) {
  // The init test script for TMCB1 should set WORD_STATUS to 42
  BOOST_TEST(test.getScalar<uint32_t>("/TMCB1/WORD_STATUS") == 42);
}

BOOST_FIXTURE_TEST_CASE(testTriggers, GenericServerFixture) {
  // check that timer has been created
  BOOST_CHECK_NO_THROW(test.getScalar<uint64_t>("msTimer/tick"));

  // check that trigger is working
  auto id1 = test.getScalar<uint32_t>("TMCB1/WORD_ID");
  auto id2 = test.getScalar<uint32_t>("TMCB2/BSP/WORD_ID");

  id1.readLatest();
  id2.readLatest();

  testApp.periodicTriggers[0].sendTrigger();
  test.stepApplication();
  // one new value on TMCB1, none on TMCB2
  BOOST_CHECK(id1.readNonBlocking());
  BOOST_CHECK(!id1.readNonBlocking());
  BOOST_CHECK(!id2.readNonBlocking());

  test.getVoid("/manual/trigger").write();
  test.stepApplication();
  // one new value on TMCB2, none on TMCB1
  BOOST_CHECK(!id1.readNonBlocking());
  BOOST_CHECK(id2.readNonBlocking());
  BOOST_CHECK(!id2.readNonBlocking());
}
