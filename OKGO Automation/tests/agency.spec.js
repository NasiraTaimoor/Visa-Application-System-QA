//TC-AG-001: Super Admin creates an Agency with valid data
const { test, expect } = require('@playwright/test');

// Paste helper here
async function fillAgencyForm(page, overrides = {}) {
  const id = Date.now();

  const data = {
    companyName: `Playwright Agency ${id}`,
    tradeName: `QA Agency ${id}`,
    registerNumber: `REG-${id}`,
    licenseNumber: `LIC-${id}`,
    legalType: 'LLC',
    mainLicenseNumber: `MAIN-${id}`,
    expiryDate: '2027-12-31',
    address: 'Business Bay, Dubai',
    city: 'Dubai',
    country: 'United Arab Emirates',
    phone: '+971501234567',
    email: `qa.agency.${id}@example.com`,
    currency: 'UAE Dirham',
    bankName: 'Emirates NBD',
    accountNumber: `ACC${id}`,
    bankCode: 'EBILAEAD',
    bankContact: 'QA Bank Contact',
    ...overrides,
  };

  await page.getByRole('textbox', { name: /^Company name$/i })
    .fill(data.companyName);

  await page.getByRole('textbox', { name: /^Trade name$/i })
    .fill(data.tradeName);

  await page.getByRole('textbox', { name: /^Register number$/i })
    .fill(data.registerNumber);

  await page.getByRole('textbox', { name: /^License number$/i })
    .fill(data.licenseNumber);

  await page.getByRole('textbox', { name: /^Legal type$/i })
    .fill(data.legalType);

  await page.getByRole('textbox', { name: /^Main license number$/i })
    .fill(data.mainLicenseNumber);

  await page.getByRole('textbox', {
    name: /^Contract expiry date$/i,
  }).fill(data.expiryDate);

  await page.getByRole('textbox', { name: /^Address$/i })
    .fill(data.address);

  await page.getByRole('textbox', { name: /^City$/i })
    .fill(data.city);

  if (data.country) {
  await page.getByRole('combobox', {
    name: /^Country$/i,
  }).click();

  await page.getByRole('option', {
    name: data.country,
    exact: true,
  }).click();
}

  await page.getByRole('textbox', { name: /^Phone number$/i })
    .fill(data.phone);

  await page.getByRole('textbox', { name: /^Email$/i })
    .fill(data.email);

  if (data.currency) {
  await page.getByRole('combobox', {
    name: /^Currency$/i,
  }).click();

  await page.getByRole('option', {
    name: data.currency,
    exact: true,
  }).click();
}

  await page.getByRole('textbox', { name: /^Bank name$/i })
    .fill(data.bankName);

  await page.getByRole('textbox', { name: /^Account number$/i })
    .fill(data.accountNumber);

  await page.getByRole('textbox', { name: /^Bank code$/i })
    .fill(data.bankCode);

  await page.getByRole('textbox', {
    name: /^Bank contact person$/i,
  }).fill(data.bankContact);

  return data;
}

// Your existing test starts below
test('Super Admin can create an Agency', async ({ page }) => {
      test.setTimeout(60_000);
  // Login
  await page.goto('http://localhost:3001/login');

  const email = process.env.OKGO_EMAIL?.trim();
const password = process.env.OKGO_PASSWORD;

if (!email || !password) {
  throw new Error('OKGO_EMAIL or OKGO_PASSWORD is missing.');
}

await page.getByLabel('Email').fill(email);
await page.getByLabel('Password').fill(password);
await page.getByRole('button', { name: 'Sign in' }).click();
await expect(page).toHaveURL(
  /\/(verify-otp|dashboard|agent)(?:\/|$)/,
  { timeout: 15_000 }
 );
  // Complete OTP when required
  if (page.url().includes('verify-otp')) {
    await page.getByLabel(/one-time code/i)
      .fill(process.env.OKGO_OTP);

    await page.getByRole('button', {
      name: /verify|continue/i,
    }).click();

    await expect(page).toHaveURL(/dashboard|agent/, {
      timeout: 15000,
    });
  }

  // Open Agency Management
await page.goto('http://localhost:3001/dashboard/agencies');

await expect(
  page.getByRole('heading', { name: 'Agency Management' })
).toBeVisible();

await fillAgencyForm(page);

const createAgencyButton = page.getByRole('button', {
  name: /^Create agency$/i,
});

await expect(createAgencyButton).toBeEnabled();

await page.screenshot({
  path: 'screenshots/agency-form-filled.png',
  fullPage: true,
});

await createAgencyButton.click();

// Update this text if the application uses a different success message.
await expect(
  page.getByText(/agency created|created successfully/i)
).toBeVisible({
  timeout: 15_000,

});
});

//TC-AG-002: Company name is required
test('TC-AG-002: Company name is required', async ({ page }) => {
  test.setTimeout(60_000);

  const email = process.env.OKGO_EMAIL?.trim();
  const password = process.env.OKGO_PASSWORD;

  if (!email || !password) {
    throw new Error('OKGO_EMAIL or OKGO_PASSWORD is missing.');
  }

  // Login
  await page.goto('http://localhost:3001/login');

  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL(
    /\/(verify-otp|dashboard|agent)(?:\/|$)/,
    { timeout: 15_000 }
  );

  // OTP
  if (page.url().includes('verify-otp')) {
    await page.getByLabel(/one-time code/i)
      .fill(process.env.OKGO_OTP);

    await page.getByRole('button', {
      name: /verify|continue/i,
    }).click();

    await expect(page).toHaveURL(/\/dashboard/, {
      timeout: 15_000,
    });
  }

  // Open Agency Management
  await page.goto('http://localhost:3001/dashboard/agencies');

  await expect(
    page.getByRole('heading', { name: 'Agency Management' })
  ).toBeVisible();

  // Fill all fields except Company name
  await fillAgencyForm(page, {
    companyName: '',
  });

  const createAgencyButton = page.getByRole('button', {
    name: /^Create agency$/i,
  });

  // Invalid form should not be submitted
const companyNameInput = page.getByRole('textbox', {
  name: /^Company name$/i,
});
await createAgencyButton.click();

await expect(companyNameInput).toHaveAttribute(
  'aria-invalid',
  'true'
);

await expect(
  page.getByRole('alert').filter({
    hasText: 'Some fields need your attention.',
  })
).toBeVisible();
await expect(
  page.getByText(/agency created|created successfully/i)
).not.toBeVisible();
  await page.screenshot({
    path: 'screenshots/company-name-required.png',
    fullPage: true,
  });
});
// TC-AG-003: Trade name is required
test('TC-AG-003: Trade name is required', async ({ page }) => {
  test.setTimeout(60_000);

  const email = process.env.OKGO_EMAIL?.trim();
  const password = process.env.OKGO_PASSWORD;

  if (!email || !password) {
    throw new Error('OKGO_EMAIL or OKGO_PASSWORD is missing.');
  }

  // Login
  await page.goto('http://localhost:3001/login');

  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL(
    /\/(verify-otp|dashboard|agent)(?:\/|$)/,
    { timeout: 15_000 }
  );

  // Complete OTP when required
  if (page.url().includes('verify-otp')) {
    const otp = process.env.OKGO_OTP;

    if (!otp) {
      throw new Error('OKGO_OTP is missing.');
    }

    await page.getByLabel(/one-time code/i).fill(otp);

    await page.getByRole('button', {
      name: /verify|continue/i,
    }).click();

    await expect(page).toHaveURL(/\/(dashboard|agent)(?:\/|$)/, {
      timeout: 15_000,
    });
  }

  // Open Agency Management
  await page.goto('http://localhost:3001/dashboard/agencies');

  await expect(
    page.getByRole('heading', { name: 'Agency Management' })
  ).toBeVisible();

  // Fill every field except Trade name
  await fillAgencyForm(page, {
    tradeName: '',
  });

  const tradeNameInput = page.getByRole('textbox', {
    name: /^Trade name$/i,
  });

  const createAgencyButton = page.getByRole('button', {
    name: /^Create agency$/i,
  });

  // Submit to trigger form validation
  await createAgencyButton.click();

  await expect(tradeNameInput).toHaveAttribute(
    'aria-invalid',
    'true'
  );

  await expect(
    page.getByRole('alert').filter({
      hasText: 'Some fields need your attention.',
    })
  ).toBeVisible();

  await expect(
    page.getByText(/agency created|created successfully/i)
  ).not.toBeVisible();

  await page.screenshot({
    path: 'screenshots/trade-name-required.png',
    fullPage: true,
  });
});
// TC-AG-004: Register number is required
test('TC-AG-004: Register number is required', async ({ page }) => {
  test.setTimeout(60_000);

  const email = process.env.OKGO_EMAIL?.trim();
  const password = process.env.OKGO_PASSWORD;

  if (!email || !password) {
    throw new Error('OKGO_EMAIL or OKGO_PASSWORD is missing.');
  }

  // Login
  await page.goto('http://localhost:3001/login');

  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL(
    /\/(verify-otp|dashboard|agent)(?:\/|$)/,
    { timeout: 15_000 }
  );

  // Complete OTP when required
  if (page.url().includes('verify-otp')) {
    const otp = process.env.OKGO_OTP;

    if (!otp) {
      throw new Error('OKGO_OTP is missing.');
    }

    await page.getByLabel(/one-time code/i).fill(otp);

    await page.getByRole('button', {
      name: /verify|continue/i,
    }).click();

    await expect(page).toHaveURL(
      /\/(dashboard|agent)(?:\/|$)/,
      { timeout: 15_000 }
    );
  }

  // Open Agency Management
  await page.goto('http://localhost:3001/dashboard/agencies');

  await expect(
    page.getByRole('heading', {
      name: 'Agency Management',
    })
  ).toBeVisible();

  // Fill every field except Register number
  await fillAgencyForm(page, {
    registerNumber: '',
  });

  const registerNumberInput = page.getByRole('textbox', {
    name: /^Register number$/i,
  });

  const createAgencyButton = page.getByRole('button', {
    name: /^Create agency$/i,
  });

  // Submit to trigger validation
  await createAgencyButton.click();

  await expect(registerNumberInput).toHaveAttribute(
    'aria-invalid',
    'true'
  );

  await expect(
    page.getByRole('alert').filter({
      hasText: 'Some fields need your attention.',
    })
  ).toBeVisible();

  await expect(
    page.getByText(/agency created|created successfully/i)
  ).not.toBeVisible();

  await page.screenshot({
    path: 'screenshots/register-number-required.png',
    fullPage: true,
  });
});
const requiredAgencyFieldCases = [
  {
    id: 'TC-AG-005',
    name: 'License number is required',
    dataKey: 'licenseNumber',
    role: 'textbox',
    label: /^License number$/i,
    screenshot: 'license-number-required.png',
  },
  {
    id: 'TC-AG-006',
    name: 'Legal type is required',
    dataKey: 'legalType',
    role: 'textbox',
    label: /^Legal type$/i,
    screenshot: 'legal-type-required.png',
  },
  {
    id: 'TC-AG-007',
    name: 'Main license number is required',
    dataKey: 'mainLicenseNumber',
    role: 'textbox',
    label: /^Main license number$/i,
    screenshot: 'main-license-number-required.png',
  },
  {
    id: 'TC-AG-008',
    name: 'Contract expiry date is required',
    dataKey: 'expiryDate',
    role: 'textbox',
    label: /^Contract expiry date$/i,
    screenshot: 'contract-expiry-date-required.png',
    expectsCustomAlert: false,
  },
  {
    id: 'TC-AG-009',
    name: 'Address is required',
    dataKey: 'address',
    role: 'textbox',
    label: /^Address$/i,
    screenshot: 'address-required.png',
  },
  {
    id: 'TC-AG-010',
    name: 'City is required',
    dataKey: 'city',
    role: 'textbox',
    label: /^City$/i,
    screenshot: 'city-required.png',
  },
  {
    id: 'TC-AG-011',
    name: 'Country is required',
    dataKey: 'country',
    role: 'combobox',
    label: /^Country$/i,
    screenshot: 'country-required.png',
  },
  {
    id: 'TC-AG-012',
    name: 'Phone number is required',
    dataKey: 'phone',
    role: 'textbox',
    label: /^Phone number$/i,
    screenshot: 'phone-number-required.png',
  },
  {
    id: 'TC-AG-013',
    name: 'Email is required',
    dataKey: 'email',
    role: 'textbox',
    label: /^Email$/i,
    screenshot: 'email-required.png',
  },
  {
    id: 'TC-AG-014',
    name: 'Currency is required',
    dataKey: 'currency',
    role: 'combobox',
    label: /^Currency$/i,
    screenshot: 'currency-required.png',
  },
  {
    id: 'TC-AG-015',
    name: 'Bank name is required',
    dataKey: 'bankName',
    role: 'textbox',
    label: /^Bank name$/i,
    screenshot: 'bank-name-required.png',
  },
  {
    id: 'TC-AG-016',
    name: 'Account number is required',
    dataKey: 'accountNumber',
    role: 'textbox',
    label: /^Account number$/i,
    screenshot: 'account-number-required.png',
  },
  {
    id: 'TC-AG-017',
    name: 'Bank code is required',
    dataKey: 'bankCode',
    role: 'textbox',
    label: /^Bank code$/i,
    screenshot: 'bank-code-required.png',
  },
  {
    id: 'TC-AG-018',
    name: 'Bank contact person is required',
    dataKey: 'bankContact',
    role: 'textbox',
    label: /^Bank contact person$/i,
    screenshot: 'bank-contact-person-required.png',
  },
];

for (const testCase of requiredAgencyFieldCases) {
  test(`${testCase.id}: ${testCase.name}`, async ({ page }) => {
    test.setTimeout(60_000);

    const email = process.env.OKGO_EMAIL?.trim();
    const password = process.env.OKGO_PASSWORD;
    const otp = process.env.OKGO_OTP;

    if (!email || !password) {
      throw new Error(
        'OKGO_EMAIL or OKGO_PASSWORD is missing.'
      );
    }

    // Login
    await page.goto('http://localhost:3001/login');

    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);

    await page.getByRole('button', {
      name: 'Sign in',
    }).click();

    await expect(page).toHaveURL(
      /\/(verify-otp|dashboard|agent)(?:\/|$)/,
      { timeout: 15_000 }
    );

    // Complete OTP when required
    if (page.url().includes('verify-otp')) {
      if (!otp) {
        throw new Error('OKGO_OTP is missing.');
      }

      await page.getByLabel(/one-time code/i).fill(otp);

      await page.getByRole('button', {
        name: /verify|continue/i,
      }).click();

      await expect(page).toHaveURL(
        /\/(dashboard|agent)(?:\/|$)/,
        { timeout: 15_000 }
      );
    }

    // Open Agency Management
    await page.goto(
      'http://localhost:3001/dashboard/agencies'
    );

    await expect(
      page.getByRole('heading', {
        name: 'Agency Management',
      })
    ).toBeVisible();

    // Fill all fields except the field being tested
    await fillAgencyForm(page, {
      [testCase.dataKey]: '',
    });

    const requiredField = page.getByRole(
      testCase.role,
      { name: testCase.label }
    );

    const createAgencyButton = page.getByRole('button', {
      name: /^Create agency$/i,
    });

    await createAgencyButton.click();

    // Confirm the tested field is empty or invalid
if (testCase.role === 'combobox') {
  await expect(requiredField).toHaveAttribute(
    'data-placeholder',
    ''
  );
} else {
  await expect(requiredField).toHaveAttribute(
    'aria-invalid',
    'true'
  );
}
if (testCase.expectsCustomAlert !== false) {
  await expect(
    page.getByRole('alert').filter({
      hasText: 'Some fields need your attention.',
    })
  ).toBeVisible();
}

    // Confirm an agency was not created
    await expect(
      page.getByText(
        /agency created|created successfully/i
      )
    ).not.toBeVisible();

    await page.screenshot({
      path: `screenshots/${testCase.screenshot}`,
      fullPage: true,
    });
});
}