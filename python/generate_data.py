"""
generate_data.py — produces data/raw/applications_raw.csv, a deliberately
messy raw export of the application log, to demonstrate real-world data
cleaning (clean_data.py reverses this). Fixed random seed -> deterministic,
reproducible output, so the pipeline runs identically every time.

The underlying application records (company, role, dates, outcomes) are the
actual log this project was built from. This script re-exports them in messy
raw form on purpose: mixed date formats, inconsistent status casing, stray
whitespace, and a few duplicate "logged it twice" rows -- exactly the kind
of mess a real job-search spreadsheet or export accumulates over months.
"""
import csv
import io
import random
from datetime import datetime

random.seed(42)

# --- master application log (embedded so this script is self-contained) ---
MASTER_CSV = """Application ID,Company,Role Title,Location,Date Applied,Source,Resume Version,Salary Min,Salary Max,Status,Response Date,Interview Date,Response Time (Days)
APP0183,Foundry Manufacturing,Business Analyst,"Denver, CO",2026-03-05,LinkedIn,Resume_B_Technical,65000,70000,Rejected,2026-03-16,,11
APP0107,Bright Path Media,Data Analyst I,"Atlanta, GA",2026-06-21,Company Website,Resume_C_BusinessFocus,68000,70000,Interview,2026-07-11,2026-07-12,20
APP0121,Bluepeak Insurance,Data Analyst,"Chicago, IL",2026-05-08,Company Website,Resume_B_Technical,48000,58000,Rejected,2026-05-11,,3
APP0051,Marlin Energy,BI Analyst,"Indianapolis, IN",2026-04-06,Company Website,Resume_C_BusinessFocus,60000,68000,No Response,,,
APP0102,Vertex Capital Partners,Marketing Data Analyst,"Indianapolis, IN",2026-04-24,Indeed,Resume_B_Technical,48000,62000,No Response,,,
APP0125,Amber Logistics,Junior Business Intelligence Analyst,"Atlanta, GA",2026-02-24,Glassdoor,Resume_A_Analytics,60000,78000,Applied,,,
APP0065,Crestline Insurance,Junior Business Intelligence Analyst,"Chicago, IL",2026-07-13,Indeed,Resume_C_BusinessFocus,52000,82000,Offer,2026-07-27,2026-07-28,14
APP0084,Fieldstone Consulting,Business Analyst,Remote,2026-05-26,Company Website,Resume_B_Technical,62000,75000,Applied,,,
APP0045,Rivergate Bank,Marketing Data Analyst,"Chicago, IL",2026-06-08,ZipRecruiter,Resume_A_Analytics,60000,82000,Interview,2026-06-22,2026-06-28,14
APP0155,Greenfield Foods,Operations Data Analyst,"Minneapolis, MN",2026-03-11,Handshake,Resume_A_Analytics,58000,65000,Applied,,,
APP0041,Bright Path Media,BI Analyst,Remote,2026-06-09,Company Website,Resume_B_Technical,62000,68000,No Response,,,
APP0025,Beacon Hill Hospital,Marketing Data Analyst,Remote,2026-03-04,Referral,Resume_A_Analytics,68000,82000,No Response,,,
APP0138,Rivergate Bank,Data Analyst I,"Chicago, IL",2026-05-05,Glassdoor,Resume_C_BusinessFocus,48000,78000,No Response,,,
APP0116,Horizon Freight,Operations Data Analyst,"Charlotte, NC",2026-08-04,Company Website,Resume_A_Analytics,62000,68000,No Response,,,
APP0086,Meridian Data Co,Reporting Analyst,"Chicago, IL",2026-03-20,LinkedIn,Resume_C_BusinessFocus,,,No Response,,,
APP0070,Amber Logistics,Junior Data Analyst,"Austin, TX",2026-06-07,Handshake,Resume_C_BusinessFocus,68000,72000,No Response,,,
APP0159,Cobalt Analytics Inc,Business Analyst,"Chicago, IL",2026-05-03,ZipRecruiter,Resume_A_Analytics,48000,70000,No Response,,,
APP0074,Marlin Energy,Business Analyst,"Atlanta, GA",2026-07-29,Glassdoor,Resume_C_BusinessFocus,55000,62000,Rejected,2026-08-11,,13
APP0146,Amber Logistics,Junior Data Analyst,"Phoenix, AZ",2026-07-07,Referral,Resume_A_Analytics,68000,72000,Rejected,2026-07-28,,21
APP0145,Union Square Bank,Junior Data Analyst,"Tampa, FL",2026-03-06,Company Website,Resume_C_BusinessFocus,,,No Response,,,
APP0036,Greenfield Foods,Data Analyst Intern,"Chicago, IL",2026-08-15,ZipRecruiter,Resume_C_BusinessFocus,58000,68000,Rejected,,,
APP0050,Granite Manufacturing,Data Analyst I,"Indianapolis, IN",2026-06-30,Indeed,Resume_B_Technical,68000,70000,Applied,,,
APP0185,Crestline Insurance,Marketing Data Analyst,"Austin, TX",2026-03-19,Glassdoor,Resume_C_BusinessFocus,68000,72000,Rejected,2026-03-25,,6
APP0156,Beacon Hill Hospital,Reporting Analyst,"Dallas, TX",2026-03-09,Company Website,Resume_A_Analytics,52000,58000,Rejected,2026-03-26,,17
APP0113,Willow Creek Health,Junior Business Intelligence Analyst,"Minneapolis, MN",2026-07-29,Referral,Resume_B_Technical,55000,70000,No Response,,,
APP0060,Sterling Healthcare Group,Data Analyst I,Remote,2026-06-14,ZipRecruiter,Resume_C_BusinessFocus,48000,58000,No Response,,,
APP0165,Elm Street Foods,Operations Data Analyst,"Denver, CO",2026-02-10,Indeed,Resume_B_Technical,,,Applied,,,
APP0175,Cypress Analytics,Data Analyst I,"Phoenix, AZ",2026-03-01,Handshake,Resume_B_Technical,55000,62000,No Response,,,
APP0072,Crestline Insurance,Reporting Analyst,"Atlanta, GA",2026-06-09,Referral,Resume_B_Technical,,,Applied,,,
APP0076,Harbor Health Systems,Junior Business Intelligence Analyst,"Atlanta, GA",2026-04-02,ZipRecruiter,Resume_C_BusinessFocus,60000,78000,Offer,2026-04-10,2026-04-22,8
APP0068,Harbor Health Systems,Junior Business Intelligence Analyst,Remote,2026-04-22,Company Website,Resume_A_Analytics,65000,75000,Rejected,2026-05-05,,13
APP0047,Vertex Capital Partners,Junior Business Intelligence Analyst,"Dallas, TX",2026-03-11,ZipRecruiter,Resume_C_BusinessFocus,48000,65000,No Response,,,
APP0056,Pioneer Energy Corp,Operations Data Analyst,"Austin, TX",2026-05-06,Company Website,Resume_B_Technical,70000,75000,Rejected,2026-05-11,,5
APP0040,Sterling Healthcare Group,BI Analyst,"Minneapolis, MN",2026-07-01,Handshake,Resume_C_BusinessFocus,,,Rejected,2026-07-09,,8
APP0166,Amber Logistics,Junior Data Analyst,"Tampa, FL",2026-02-19,Referral,Resume_B_Technical,62000,65000,No Response,,,
APP0082,Bright Path Media,Data Analyst,"Denver, CO",2026-03-24,Indeed,Resume_A_Analytics,62000,70000,Interview,2026-04-11,2026-04-06,18
APP0103,Harbor Health Systems,Junior Business Intelligence Analyst,"Minneapolis, MN",2026-08-11,Company Website,Resume_A_Analytics,,,Offer,,,
APP0029,Fieldstone Consulting,Business Analyst,"Tampa, FL",2026-02-13,Company Website,Resume_A_Analytics,62000,68000,No Response,,,
APP0023,Quartz Data Solutions,Marketing Data Analyst,"Minneapolis, MN",2026-03-16,Handshake,Resume_C_BusinessFocus,60000,82000,Rejected,2026-04-05,,20
APP0022,Greenfield Foods,Junior Business Intelligence Analyst,"Indianapolis, IN",2026-08-11,Company Website,Resume_C_BusinessFocus,60000,75000,Interview,2026-08-12,,1
APP0011,Vertex Capital Partners,Junior Business Intelligence Analyst,"Columbus, OH",2026-07-19,LinkedIn,Resume_A_Analytics,65000,75000,No Response,,,
APP0042,Meridian Data Co,Data Analyst I,Remote,2026-06-01,Handshake,Resume_A_Analytics,68000,70000,No Response,,,
APP0009,Stonebridge Consulting,Junior Business Intelligence Analyst,"Columbus, OH",2026-07-27,Referral,Resume_C_BusinessFocus,60000,75000,Applied,,,
APP0160,Solstice Software,Junior Data Analyst,Remote,2026-03-06,LinkedIn,Resume_A_Analytics,65000,72000,Applied,,,
APP0142,Bright Path Media,Data Analyst Intern,"Tampa, FL",2026-05-13,LinkedIn,Resume_C_BusinessFocus,65000,68000,Applied,,,
APP0144,Clearwater Media,Data Analyst,"Dallas, TX",2026-08-05,ZipRecruiter,Resume_B_Technical,58000,75000,Rejected,2026-08-09,,4
APP0008,Elm Street Foods,Data Analyst,"Chicago, IL",2026-04-03,Glassdoor,Resume_B_Technical,52000,62000,Applied,,,
APP0048,Lighthouse Retail Group,Data Analyst Intern,Remote,2026-07-17,ZipRecruiter,Resume_B_Technical,62000,82000,Applied,,,
APP0131,Fieldstone Consulting,Junior Data Analyst,Remote,2026-03-29,LinkedIn,Resume_B_Technical,70000,82000,No Response,,,
APP0181,Ironclad Manufacturing,Marketing Data Analyst,"Chicago, IL",2026-07-14,Glassdoor,Resume_B_Technical,60000,70000,No Response,,,
APP0139,Rivergate Bank,Reporting Analyst,"Columbus, OH",2026-07-01,Handshake,Resume_C_BusinessFocus,65000,65000,Rejected,2026-07-08,,7
APP0184,Marlin Energy,BI Analyst,"Charlotte, NC",2026-06-01,Handshake,Resume_A_Analytics,52000,78000,Applied,,,
APP0024,Harbor Health Systems,Reporting Analyst,"Charlotte, NC",2026-05-28,Referral,Resume_A_Analytics,58000,75000,No Response,,,
APP0091,Redwood Consulting,Marketing Data Analyst,"Columbus, OH",2026-05-15,Handshake,Resume_C_BusinessFocus,,,No Response,,,
APP0003,Trailhead Logistics,Junior Data Analyst,"Dallas, TX",2026-04-17,LinkedIn,Resume_C_BusinessFocus,62000,68000,Rejected,2026-04-19,,2
APP0069,Marlin Energy,Junior Business Intelligence Analyst,"Phoenix, AZ",2026-04-21,LinkedIn,Resume_B_Technical,58000,72000,Rejected,2026-04-24,,3
APP0109,Summit Consulting Partners,Operations Data Analyst,Remote,2026-02-09,LinkedIn,Resume_B_Technical,55000,65000,No Response,,,
APP0007,Foundry Manufacturing,Data Analyst,"Indianapolis, IN",2026-07-25,ZipRecruiter,Resume_A_Analytics,,,Interview,2026-08-08,2026-08-13,14
APP0182,Beacon Financial Group,Marketing Data Analyst,"Denver, CO",2026-05-15,Glassdoor,Resume_B_Technical,48000,68000,No Response,,,
APP0063,Horizon Freight,Business Analyst,"Phoenix, AZ",2026-06-24,LinkedIn,Resume_C_BusinessFocus,52000,75000,Rejected,2026-07-08,,14
APP0163,Trailhead Logistics,Data Analyst,"Dallas, TX",2026-05-03,Handshake,Resume_C_BusinessFocus,68000,72000,No Response,,,
APP0019,Parallax Software,Reporting Analyst,"Denver, CO",2026-02-28,Indeed,Resume_C_BusinessFocus,48000,78000,No Response,,,
APP0115,Union Square Bank,BI Analyst,Remote,2026-08-09,Indeed,Resume_A_Analytics,68000,68000,Applied,,,
APP0128,Union Square Bank,Marketing Data Analyst,"Atlanta, GA",2026-07-03,Company Website,Resume_C_BusinessFocus,62000,68000,Applied,,,
APP0122,Summit Consulting Partners,BI Analyst,"Phoenix, AZ",2026-02-09,Referral,Resume_C_BusinessFocus,58000,62000,Applied,,,
APP0180,Meridian Data Co,Junior Business Intelligence Analyst,"Dallas, TX",2026-05-29,Handshake,Resume_B_Technical,68000,70000,No Response,,,
APP0100,Skyline Retailers,Data Analyst Intern,"Minneapolis, MN",2026-04-16,Handshake,Resume_A_Analytics,52000,72000,Applied,,,
APP0073,Cypress Analytics,Business Analyst,"Atlanta, GA",2026-05-11,Glassdoor,Resume_B_Technical,58000,62000,No Response,,,
APP0119,Cypress Analytics,Marketing Data Analyst,"Indianapolis, IN",2026-02-02,Company Website,Resume_A_Analytics,,,No Response,,,
APP0098,Parallax Software,Business Analyst,"Dallas, TX",2026-05-17,ZipRecruiter,Resume_A_Analytics,58000,68000,No Response,,,
APP0095,Ironclad Manufacturing,Junior Business Intelligence Analyst,"Atlanta, GA",2026-06-23,Handshake,Resume_B_Technical,55000,68000,Interview,2026-07-06,2026-06-29,13
APP0162,Copper Ridge Insurance,Business Analyst,Remote,2026-07-08,Referral,Resume_C_BusinessFocus,60000,78000,No Response,,,
APP0114,Solstice Software,Junior Business Intelligence Analyst,"Columbus, OH",2026-04-26,Glassdoor,Resume_A_Analytics,,,Rejected,2026-05-03,,7
APP0001,Rivergate Bank,Data Analyst,Remote,2026-03-30,Glassdoor,Resume_A_Analytics,,,Applied,,,
APP0031,Clearwater Media,Data Analyst I,Remote,2026-03-02,ZipRecruiter,Resume_C_BusinessFocus,,,Rejected,2026-03-03,,1
APP0148,Anchor Insurance Services,Data Analyst,"Minneapolis, MN",2026-06-07,Handshake,Resume_A_Analytics,58000,78000,No Response,,,
APP0062,Sterling Healthcare Group,Junior Business Intelligence Analyst,"Atlanta, GA",2026-05-14,Handshake,Resume_B_Technical,52000,72000,No Response,,,
APP0118,Trailhead Logistics,Data Analyst,"Phoenix, AZ",2026-07-22,LinkedIn,Resume_A_Analytics,,,Applied,,,
APP0168,Amber Logistics,Data Analyst Intern,Remote,2026-04-30,LinkedIn,Resume_A_Analytics,55000,62000,Offer,2026-05-21,2026-05-19,21
APP0112,Cascade Retail Co,Business Analyst,"Phoenix, AZ",2026-08-07,Glassdoor,Resume_A_Analytics,62000,68000,Rejected,2026-08-12,,5
APP0140,Anchor Insurance Services,BI Analyst,Remote,2026-07-24,Glassdoor,Resume_C_BusinessFocus,55000,75000,Rejected,2026-08-02,,9
APP0021,Fieldstone Consulting,Data Analyst,"Phoenix, AZ",2026-07-26,Handshake,Resume_C_BusinessFocus,58000,72000,Rejected,2026-08-06,,11
APP0038,Crestline Insurance,Data Analyst,"Austin, TX",2026-04-19,Indeed,Resume_C_BusinessFocus,58000,62000,Applied,,,
APP0053,Bluepeak Insurance,BI Analyst,"Atlanta, GA",2026-03-17,ZipRecruiter,Resume_B_Technical,70000,72000,Applied,,,
APP0046,Marlin Energy,Marketing Data Analyst,"Tampa, FL",2026-06-18,Indeed,Resume_B_Technical,62000,82000,No Response,,,
APP0147,Fieldstone Consulting,Data Analyst Intern,"Minneapolis, MN",2026-04-12,Indeed,Resume_A_Analytics,58000,82000,Rejected,2026-05-02,,20
APP0108,Copper Ridge Insurance,Data Analyst,"Charlotte, NC",2026-05-18,Indeed,Resume_C_BusinessFocus,48000,82000,No Response,,,
APP0143,Cascade Retail Co,Data Analyst,"Chicago, IL",2026-02-05,ZipRecruiter,Resume_B_Technical,55000,78000,Applied,,,
APP0150,Skyline Retailers,Junior Data Analyst,"Indianapolis, IN",2026-07-08,Referral,Resume_C_BusinessFocus,,,Applied,,,
APP0105,Skyline Retailers,Junior Business Intelligence Analyst,"Phoenix, AZ",2026-05-14,Glassdoor,Resume_A_Analytics,55000,65000,Rejected,2026-05-22,,8
APP0026,Pioneer Energy Corp,BI Analyst,"Minneapolis, MN",2026-06-05,Handshake,Resume_C_BusinessFocus,,,Rejected,2026-06-15,,10
APP0177,Elm Street Foods,Junior Data Analyst,"Tampa, FL",2026-04-18,Indeed,Resume_A_Analytics,68000,72000,Offer,2026-05-02,2026-04-29,14
APP0101,Marlin Energy,Reporting Analyst,"Columbus, OH",2026-06-16,LinkedIn,Resume_C_BusinessFocus,,,No Response,,,
APP0015,Solstice Software,BI Analyst,"Charlotte, NC",2026-02-03,Glassdoor,Resume_A_Analytics,52000,62000,No Response,,,
APP0037,Solstice Software,BI Analyst,Remote,2026-04-16,LinkedIn,Resume_C_BusinessFocus,,,Rejected,2026-04-17,,1
APP0124,Cobalt Analytics Inc,Data Analyst,"Indianapolis, IN",2026-06-06,Glassdoor,Resume_B_Technical,70000,75000,No Response,,,
APP0106,Horizon Freight,Reporting Analyst,Remote,2026-05-31,ZipRecruiter,Resume_A_Analytics,65000,82000,No Response,,,
APP0093,Crestline Insurance,Data Analyst Intern,"Columbus, OH",2026-06-08,Handshake,Resume_A_Analytics,68000,78000,Offer,2026-06-24,2026-06-15,16
APP0158,Clearwater Media,Marketing Data Analyst,"Charlotte, NC",2026-03-03,Glassdoor,Resume_B_Technical,58000,78000,No Response,,,
APP0014,Summit Consulting Partners,Data Analyst I,"Chicago, IL",2026-05-15,ZipRecruiter,Resume_A_Analytics,58000,58000,Applied,,,
APP0154,Beacon Hill Hospital,Data Analyst,"Dallas, TX",2026-04-14,LinkedIn,Resume_B_Technical,,,Rejected,2026-04-29,,15
APP0018,Horizon Freight,Data Analyst,"Atlanta, GA",2026-04-05,Indeed,Resume_C_BusinessFocus,62000,82000,Rejected,2026-04-19,,14
APP0120,Ironclad Manufacturing,Operations Data Analyst,"Austin, TX",2026-07-09,Indeed,Resume_A_Analytics,62000,70000,No Response,,,
APP0078,Bluepeak Insurance,Data Analyst Intern,"Columbus, OH",2026-02-26,LinkedIn,Resume_B_Technical,,,Interview,2026-03-08,2026-03-25,10
APP0171,Skyline Retailers,Data Analyst I,"Phoenix, AZ",2026-03-12,Handshake,Resume_B_Technical,,,Applied,,,
APP0157,Crestline Insurance,Data Analyst,"Dallas, TX",2026-04-02,ZipRecruiter,Resume_A_Analytics,62000,75000,No Response,,,
APP0067,Stonebridge Consulting,Data Analyst,Remote,2026-03-27,Indeed,Resume_B_Technical,60000,70000,Rejected,2026-03-28,,1
APP0111,Amber Logistics,BI Analyst,"Columbus, OH",2026-02-09,ZipRecruiter,Resume_A_Analytics,58000,65000,Rejected,2026-02-12,,3
APP0167,Marlin Energy,Business Analyst,"Dallas, TX",2026-07-27,Glassdoor,Resume_C_BusinessFocus,55000,58000,No Response,,,
APP0085,Amber Logistics,Data Analyst I,"Indianapolis, IN",2026-02-09,Handshake,Resume_B_Technical,58000,72000,Applied,,,
APP0127,Clearwater Media,Junior Business Intelligence Analyst,"Denver, CO",2026-06-04,Company Website,Resume_B_Technical,62000,70000,Rejected,2026-06-25,,21
APP0039,Fieldstone Consulting,BI Analyst,Remote,2026-07-07,Referral,Resume_A_Analytics,52000,68000,Offer,2026-07-16,2026-07-17,9
APP0176,Meridian Data Co,Junior Business Intelligence Analyst,"Austin, TX",2026-07-25,Referral,Resume_C_BusinessFocus,48000,75000,Rejected,2026-08-05,,11
APP0081,Ironclad Manufacturing,Data Analyst I,Remote,2026-03-07,Handshake,Resume_B_Technical,70000,72000,Applied,,,
APP0152,Solstice Software,BI Analyst,Remote,2026-04-27,LinkedIn,Resume_A_Analytics,,,Rejected,2026-05-16,,19
APP0172,Skyline Retailers,Marketing Data Analyst,"Charlotte, NC",2026-02-24,ZipRecruiter,Resume_B_Technical,65000,65000,Rejected,2026-03-09,,13
APP0169,Elm Street Foods,Junior Business Intelligence Analyst,"Atlanta, GA",2026-02-26,Referral,Resume_B_Technical,58000,65000,Rejected,2026-02-28,,2
APP0020,Meridian Data Co,Data Analyst Intern,"Indianapolis, IN",2026-07-24,Referral,Resume_B_Technical,70000,72000,Offer,2026-07-28,2026-08-03,4
APP0090,Cypress Analytics,Data Analyst I,"Atlanta, GA",2026-02-11,Handshake,Resume_C_BusinessFocus,,,Rejected,2026-03-04,,21
APP0061,Meridian Data Co,Data Analyst I,"Indianapolis, IN",2026-08-02,Referral,Resume_C_BusinessFocus,70000,70000,No Response,,,
APP0033,Fieldstone Consulting,Business Analyst,Remote,2026-04-11,Referral,Resume_C_BusinessFocus,70000,78000,Rejected,2026-04-30,,19
APP0071,Summit Consulting Partners,BI Analyst,"Charlotte, NC",2026-02-15,Company Website,Resume_A_Analytics,60000,62000,No Response,,,
APP0016,Beacon Hill Hospital,Data Analyst,"Indianapolis, IN",2026-04-18,Handshake,Resume_C_BusinessFocus,52000,65000,Interview,2026-04-22,2026-05-01,4
APP0149,Vantage Point Capital,Marketing Data Analyst,"Minneapolis, MN",2026-07-01,LinkedIn,Resume_A_Analytics,,,Applied,,,
APP0057,Copper Ridge Insurance,Reporting Analyst,"Tampa, FL",2026-07-26,Glassdoor,Resume_A_Analytics,58000,62000,No Response,,,
APP0054,Sterling Healthcare Group,Junior Business Intelligence Analyst,"Tampa, FL",2026-05-05,Handshake,Resume_C_BusinessFocus,58000,65000,Applied,,,
APP0030,Willow Creek Health,Reporting Analyst,"Indianapolis, IN",2026-02-11,LinkedIn,Resume_C_BusinessFocus,58000,68000,Rejected,2026-03-03,,20
APP0132,Anchor Insurance Services,Junior Business Intelligence Analyst,"Chicago, IL",2026-03-09,LinkedIn,Resume_C_BusinessFocus,62000,78000,No Response,,,
APP0141,Crestline Insurance,BI Analyst,"Indianapolis, IN",2026-05-27,Company Website,Resume_B_Technical,52000,75000,Applied,,,
APP0028,Trailhead Logistics,Data Analyst I,"Columbus, OH",2026-04-11,Company Website,Resume_A_Analytics,48000,75000,No Response,,,
APP0133,Union Square Bank,Junior Data Analyst,"Indianapolis, IN",2026-08-09,Handshake,Resume_A_Analytics,,,No Response,,,
APP0013,Cascade Retail Co,Business Analyst,"Dallas, TX",2026-04-09,LinkedIn,Resume_B_Technical,68000,70000,Interview,2026-04-27,2026-04-18,18
APP0066,Fieldstone Consulting,Marketing Data Analyst,Remote,2026-04-11,Company Website,Resume_B_Technical,62000,70000,Applied,,,
APP0097,Lighthouse Retail Group,Data Analyst I,Remote,2026-02-14,Indeed,Resume_C_BusinessFocus,55000,82000,Rejected,2026-03-06,,20
APP0094,Lighthouse Retail Group,Data Analyst Intern,"Minneapolis, MN",2026-02-12,Company Website,Resume_B_Technical,68000,70000,No Response,,,
APP0032,Stonebridge Consulting,Junior Data Analyst,"Minneapolis, MN",2026-04-30,Referral,Resume_A_Analytics,62000,62000,No Response,,,
APP0044,Elm Street Foods,Marketing Data Analyst,"Minneapolis, MN",2026-04-10,LinkedIn,Resume_A_Analytics,60000,78000,No Response,,,
APP0130,Amber Logistics,Junior Business Intelligence Analyst,"Minneapolis, MN",2026-05-26,Company Website,Resume_A_Analytics,68000,75000,Offer,2026-06-09,2026-06-11,14
APP0006,Skyline Retailers,Data Analyst Intern,"Columbus, OH",2026-06-07,Indeed,Resume_C_BusinessFocus,,,Applied,,,
APP0055,Horizon Freight,Junior Data Analyst,"Indianapolis, IN",2026-02-07,Indeed,Resume_B_Technical,70000,72000,Rejected,2026-02-15,,8
APP0170,Summit Consulting Partners,Operations Data Analyst,"Chicago, IL",2026-07-08,Glassdoor,Resume_C_BusinessFocus,48000,75000,Interview,2026-07-14,2026-07-18,6
APP0173,Ironclad Manufacturing,Junior Data Analyst,"Indianapolis, IN",2026-05-17,Glassdoor,Resume_C_BusinessFocus,,,Offer,2026-05-30,2026-06-08,13
APP0059,Trailhead Logistics,BI Analyst,"Minneapolis, MN",2026-07-20,Indeed,Resume_A_Analytics,55000,58000,Interview,2026-07-28,2026-07-25,8
APP0178,Greenfield Foods,Data Analyst,"Columbus, OH",2026-02-13,LinkedIn,Resume_B_Technical,58000,70000,Interview,2026-02-28,2026-03-10,15
APP0110,Willow Creek Health,Junior Data Analyst,"Austin, TX",2026-06-16,Referral,Resume_B_Technical,58000,58000,Applied,,,
APP0164,Vertex Capital Partners,Operations Data Analyst,"Atlanta, GA",2026-04-01,Handshake,Resume_C_BusinessFocus,52000,68000,Offer,2026-04-10,2026-04-13,9
APP0179,Crestline Insurance,Reporting Analyst,"Tampa, FL",2026-03-30,Indeed,Resume_C_BusinessFocus,60000,75000,Rejected,2026-03-31,,1
APP0092,Solstice Software,Data Analyst Intern,"Phoenix, AZ",2026-04-23,Referral,Resume_A_Analytics,52000,70000,No Response,,,
APP0126,Bluepeak Insurance,Data Analyst Intern,"Phoenix, AZ",2026-07-04,LinkedIn,Resume_C_BusinessFocus,58000,65000,Rejected,2026-07-17,,13
APP0088,Skyline Retailers,Marketing Data Analyst,"Phoenix, AZ",2026-06-28,Company Website,Resume_B_Technical,62000,62000,Applied,,,
APP0035,Beacon Financial Group,Junior Data Analyst,"Denver, CO",2026-07-28,Indeed,Resume_B_Technical,62000,78000,No Response,,,
APP0087,Copper Ridge Insurance,Business Analyst,Remote,2026-07-25,Company Website,Resume_A_Analytics,62000,72000,Offer,2026-08-12,2026-08-08,18
APP0135,Cypress Analytics,Junior Business Intelligence Analyst,Remote,2026-05-02,LinkedIn,Resume_B_Technical,55000,70000,Interview,2026-05-21,2026-05-28,19
APP0153,Rivergate Bank,Reporting Analyst,Remote,2026-02-12,Referral,Resume_A_Analytics,,,Interview,2026-02-24,2026-02-21,12
APP0134,Greenfield Foods,Marketing Data Analyst,Remote,2026-02-02,Company Website,Resume_B_Technical,58000,70000,Rejected,2026-02-05,,3
APP0117,Greenfield Foods,Data Analyst Intern,"Columbus, OH",2026-04-04,Company Website,Resume_C_BusinessFocus,62000,70000,No Response,,,
APP0075,Beacon Financial Group,Data Analyst Intern,"Denver, CO",2026-04-29,Indeed,Resume_A_Analytics,68000,68000,Interview,2026-05-04,2026-05-06,5
APP0077,Foundry Manufacturing,Junior Data Analyst,Remote,2026-03-04,Handshake,Resume_C_BusinessFocus,55000,70000,No Response,,,
APP0012,Greenfield Foods,Operations Data Analyst,"Charlotte, NC",2026-03-19,Indeed,Resume_B_Technical,58000,62000,No Response,,,
APP0017,Lighthouse Retail Group,Business Analyst,Remote,2026-07-31,Company Website,Resume_C_BusinessFocus,,,No Response,,,
APP0043,Elm Street Foods,BI Analyst,"Indianapolis, IN",2026-02-10,Company Website,Resume_C_BusinessFocus,62000,70000,No Response,,,
APP0079,Rivergate Bank,Data Analyst,"Columbus, OH",2026-07-10,Company Website,Resume_C_BusinessFocus,52000,78000,No Response,,,
APP0151,Fieldstone Consulting,Reporting Analyst,Remote,2026-05-23,Indeed,Resume_A_Analytics,48000,70000,Applied,,,
APP0129,Meridian Data Co,Junior Business Intelligence Analyst,"Atlanta, GA",2026-03-24,LinkedIn,Resume_C_BusinessFocus,65000,70000,Rejected,2026-04-11,,18
APP0027,Summit Consulting Partners,Junior Business Intelligence Analyst,"Dallas, TX",2026-05-31,Glassdoor,Resume_C_BusinessFocus,58000,75000,No Response,,,
APP0034,Elm Street Foods,Data Analyst Intern,"Austin, TX",2026-05-02,Company Website,Resume_A_Analytics,62000,70000,Rejected,2026-05-11,,9
APP0080,Willow Creek Health,Reporting Analyst,Remote,2026-07-21,Company Website,Resume_A_Analytics,,,Rejected,2026-08-07,,17
APP0089,Beacon Hill Hospital,Business Analyst,"Denver, CO",2026-04-24,Indeed,Resume_A_Analytics,58000,72000,Interview,2026-05-11,2026-05-01,17
APP0058,Union Square Bank,Reporting Analyst,"Austin, TX",2026-03-25,Handshake,Resume_C_BusinessFocus,68000,70000,Applied,,,
APP0064,Ironclad Manufacturing,Data Analyst Intern,"Tampa, FL",2026-03-02,Referral,Resume_B_Technical,58000,75000,Rejected,2026-03-22,,20
APP0161,Copper Ridge Insurance,Business Analyst,"Chicago, IL",2026-03-04,Handshake,Resume_B_Technical,,,Applied,,,
APP0174,Greenfield Foods,Business Analyst,Remote,2026-07-25,Company Website,Resume_A_Analytics,55000,70000,No Response,,,
APP0005,Skyline Retailers,BI Analyst,"Chicago, IL",2026-08-03,Indeed,Resume_C_BusinessFocus,68000,75000,No Response,,,
APP0049,Bluepeak Insurance,Junior Business Intelligence Analyst,"Chicago, IL",2026-07-31,Handshake,Resume_C_BusinessFocus,65000,68000,Interview,2026-08-01,2026-08-15,1
APP0136,Elm Street Foods,Operations Data Analyst,Remote,2026-06-23,ZipRecruiter,Resume_A_Analytics,60000,65000,Applied,,,
APP0083,Vantage Point Capital,Marketing Data Analyst,Remote,2026-06-13,Company Website,Resume_B_Technical,,,No Response,,,
APP0004,Nimbus Cloud Systems,BI Analyst,Remote,2026-02-19,ZipRecruiter,Resume_C_BusinessFocus,55000,82000,Rejected,2026-02-25,,6
APP0096,Quartz Data Solutions,Operations Data Analyst,"Phoenix, AZ",2026-06-25,Company Website,Resume_C_BusinessFocus,48000,72000,No Response,,,
APP0052,Crestline Insurance,Data Analyst,Remote,2026-04-15,ZipRecruiter,Resume_B_Technical,58000,72000,Rejected,2026-04-22,,7
APP0137,Elm Street Foods,Junior Business Intelligence Analyst,Remote,2026-06-06,Handshake,Resume_B_Technical,48000,68000,Applied,,,
APP0010,Northwind Analytics,Junior Data Analyst,Remote,2026-03-31,ZipRecruiter,Resume_A_Analytics,,,Applied,,,
APP0002,Marlin Energy,BI Analyst,"Minneapolis, MN",2026-08-14,Handshake,Resume_A_Analytics,65000,72000,Rejected,,,
APP0099,Lighthouse Retail Group,Data Analyst I,"Charlotte, NC",2026-04-13,Indeed,Resume_A_Analytics,58000,70000,Rejected,2026-04-20,,7
APP0123,Trailhead Logistics,Data Analyst Intern,"Dallas, TX",2026-03-08,Handshake,Resume_C_BusinessFocus,52000,82000,Rejected,2026-03-20,,12
APP0104,Bright Path Media,BI Analyst,"Columbus, OH",2026-04-26,Handshake,Resume_A_Analytics,68000,70000,Applied,,,

"""

DATE_FORMATS = ["%m/%d/%Y", "%Y-%m-%d", "%d-%b-%Y"]
STATUS_CASINGS = [str.upper, str.lower, str.title, lambda s: s]


def messify_date(value):
    if not value:
        return ""
    dt = datetime.strptime(value, "%Y-%m-%d")
    fmt = random.choice(DATE_FORMATS)
    return dt.strftime(fmt)


def messify_status(value):
    casing = random.choice(STATUS_CASINGS)
    return casing(value)


def main():
    reader = csv.DictReader(io.StringIO(MASTER_CSV))
    fieldnames = reader.fieldnames
    rows = list(reader)

    messy_rows = []
    for row in rows:
        row = dict(row)
        row["Date Applied"] = messify_date(row["Date Applied"])
        row["Response Date"] = messify_date(row["Response Date"])
        row["Interview Date"] = messify_date(row["Interview Date"])
        row["Status"] = messify_status(row["Status"])
        # stray leading/trailing whitespace on ~10% of company names
        if random.random() < 0.10:
            row["Company"] = f"  {row['Company']}  "
        # a few rows keep blanks as the literal string "N/A" instead of empty
        for col in ("Response Date", "Interview Date", "Response Time (Days)"):
            if row[col] == "" and random.random() < 0.5:
                row[col] = "N/A"
        messy_rows.append(row)

    # duplicate a handful of rows verbatim -- "logged it twice" data-entry
    # mistake, which clean_data.py needs to catch and drop
    dupes = random.sample(messy_rows, 4)
    messy_rows.extend(dupes)
    random.shuffle(messy_rows)

    with open("data/raw/applications_raw.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(messy_rows)

    print(f"Wrote {len(messy_rows)} raw rows "
          f"({len(rows)} unique + {len(dupes)} duplicates) "
          "to data/raw/applications_raw.csv")


if __name__ == "__main__":
    main()
