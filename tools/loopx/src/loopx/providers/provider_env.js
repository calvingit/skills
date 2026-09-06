const ZERO_COST = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 };

function parseJson(name, fallback) {
  const value = process.env[name];
  if (!value) return fallback;
  try {
    return JSON.parse(value);
  } catch (error) {
    throw new Error(`${name} must contain valid JSON: ${error.message}`);
  }
}

function envBoolean(name, fallback) {
  const value = process.env[name];
  if (value === undefined) return fallback;
  return /^(1|true|yes)$/i.test(value);
}

export default function providerFromEnvironment(pi) {
  const baseUrl = process.env.PI_SKILLS_PROVIDER_BASE_URL;
  const rawModels = parseJson("PI_SKILLS_PROVIDER_MODELS_JSON", null);
  if (!baseUrl && !rawModels) return;
  if (!baseUrl || !Array.isArray(rawModels) || rawModels.length === 0) {
    throw new Error(
      "PI_SKILLS_PROVIDER_BASE_URL and a non-empty PI_SKILLS_PROVIDER_MODELS_JSON are required together",
    );
  }

  const models = rawModels.map((model) => {
    if (!model || typeof model.id !== "string" || !model.id) {
      throw new Error("each PI_SKILLS_PROVIDER_MODELS_JSON entry requires a non-empty id");
    }
    return {
      id: model.id,
      name: model.name ?? model.id,
      reasoning: model.reasoning ?? false,
      input: model.input ?? ["text"],
      cost: model.cost ?? ZERO_COST,
      contextWindow: model.contextWindow ?? 128000,
      maxTokens: model.maxTokens ?? 8192,
      ...(model.compat ? { compat: model.compat } : {}),
    };
  });
  const apiKey = process.env.PI_SKILLS_PROVIDER_API_KEY;
  const headers = parseJson("PI_SKILLS_PROVIDER_HEADERS_JSON", undefined);
  const compat = parseJson("PI_SKILLS_PROVIDER_COMPAT_JSON", undefined);
  delete process.env.PI_SKILLS_PROVIDER_API_KEY;
  delete process.env.PI_SKILLS_PROVIDER_HEADERS_JSON;
  delete process.env.PI_SKILLS_PROVIDER_COMPAT_JSON;

  pi.registerProvider(process.env.PI_SKILLS_PROVIDER_NAME ?? "pi-skills-env", {
    baseUrl,
    api: process.env.PI_SKILLS_PROVIDER_API ?? "openai-completions",
    ...(apiKey ? { apiKey } : {}),
    authHeader: envBoolean("PI_SKILLS_PROVIDER_AUTH_HEADER", true),
    ...(headers ? { headers } : {}),
    ...(compat ? { compat } : {}),
    models,
  });
}
