// src/config.local.js
// This file is for local overrides. It is not committed to git.

export const DEFAULT_PARAMS = {
    putTickers: 'PLTR,CEG,CLS,CRDO,AVAV,STRL,MP,NNE,VST,NEE,D,WMB,KMI,ENB,DUK,GEV',
    callTickers: 'AVGO,GRAB,IREN,NVTS,QQQ,ARKX',
    filters: {
    DTE_MIN: 0,
    DTE_MAX: 30,
    MIN_VOLUME: 100,
    MIN_OPEN_INTEREST: 500,
    PUT_DELTA_MIN: 0,
    PUT_DELTA_MAX: 0.30,
    CALL_DELTA_MIN: 0,
    CALL_DELTA_MAX: 0.30,
    PUT_OTM_PERCENT_MIN: 5.0,
    PUT_OTM_PERCENT_MAX: 15.0,
    CALL_OTM_PERCENT_MIN: 5.0,
    CALL_OTM_PERCENT_MAX: 15.0,
  }
};
