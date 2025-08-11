// src/config.js
import { DEFAULT_PARAMS as publicParams } from './config.public.js';
import { DEFAULT_PARAMS as localParams } from './config.local.js';

export const DEFAULT_PARAMS = {
  ...publicParams,
  ...localParams,
  filters: {
    ...publicParams.filters,
    ...(localParams.filters || {}),
  },
};
