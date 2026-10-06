module.exports = ({ config }) => {
  const organization = process.env.SENTRY_ORG ?? "grande-corpo";
  const project = process.env.SENTRY_PROJECT ?? "kickoff-app";
  if (!organization || !project) return config;

  return {
    ...config,
    plugins: [
      ...(config.plugins || []),
      ["@sentry/react-native/expo", { organization, project, url: "https://sentry.io/" }],
    ],
  };
};
