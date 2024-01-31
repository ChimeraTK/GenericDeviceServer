// SPDX-FileCopyrightText: Deutsches Elektronen-Synchrotron DESY, MSK, ChimeraTK Project <chimeratk-support@desy.de>
// SPDX-License-Identifier: LGPL-3.0-or-later

#include "GenericApp.h"

#include <ChimeraTK/ApplicationCore/EnableXMLGenerator.h>
#include <ChimeraTK/ControlSystemAdapter/ApplicationFactory.h>

static ChimeraTK::ApplicationFactory<GenericApp> theFactory;
