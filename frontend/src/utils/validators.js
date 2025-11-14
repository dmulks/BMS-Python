/**
 * Validate email address
 * @param {string} email - Email address to validate
 * @returns {boolean} True if valid
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} Validation result with isValid and message
 */
export const validatePassword = (password) => {
  if (!password) {
    return { isValid: false, message: 'Password is required' };
  }

  if (password.length < 8) {
    return { isValid: false, message: 'Password must be at least 8 characters' };
  }

  if (!/[A-Z]/.test(password)) {
    return { isValid: false, message: 'Password must contain an uppercase letter' };
  }

  if (!/[a-z]/.test(password)) {
    return { isValid: false, message: 'Password must contain a lowercase letter' };
  }

  if (!/[0-9]/.test(password)) {
    return { isValid: false, message: 'Password must contain a number' };
  }

  return { isValid: true, message: 'Password is strong' };
};

/**
 * Validate phone number
 * @param {string} phone - Phone number to validate
 * @returns {boolean} True if valid
 */
export const isValidPhone = (phone) => {
  const phoneRegex = /^[\d\s\-\+\(\)]+$/;
  return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
};

/**
 * Validate date is not in the future
 * @param {string|Date} date - Date to validate
 * @returns {boolean} True if not in future
 */
export const isNotFutureDate = (date) => {
  return new Date(date) <= new Date();
};

/**
 * Validate positive number
 * @param {number} value - Value to validate
 * @returns {boolean} True if positive
 */
export const isPositiveNumber = (value) => {
  return !isNaN(value) && parseFloat(value) > 0;
};

/**
 * Validate discount rate (0-1)
 * @param {number} rate - Rate to validate
 * @returns {boolean} True if valid
 */
export const isValidDiscountRate = (rate) => {
  return !isNaN(rate) && parseFloat(rate) >= 0 && parseFloat(rate) <= 1;
};
