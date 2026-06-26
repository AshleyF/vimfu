export default {
  testEnvironment: 'node',
  transform: {},
  testMatch: ['<rootDir>/test/**/*.test.js'],
  testPathIgnorePatterns: ['/node_modules/', '\\.pw\\.test\\.js$'],
  moduleFileExtensions: ['js', 'mjs'],
};
