--------------------------
-- Collect AI papers
--------------------------
CREATE TEMP TABLE top_aiconf_papers DISTKEY(paperid) SORTKEY(paperid) AS
SELECT p.paperid,  p.doi, p.paper_title, p.year, p.date,
    'Top Conference' doc_type, p.conference_series_id, s.normalizedname conf_series, p.conference_instance_id, c.normalizedname conf_name,
    p.journal_id, j.normalizedname journal_name,
    p.citationcount, p.estimated_citation_count
FROM mag_ext.papers_pq p
LEFT JOIN 
    mag_ext.conferenceseries_pq s ON p.conference_series_id=s.conferenceseriesid
LEFT JOIN 
  mag_ext.conferenceinstances_pq c ON p.conference_instance_id=c.conferenceinstanceid
LEFT JOIN 
  mag_ext.journals_pq j ON p.journal_id=j.journalid
WHERE p.conference_series_id  in (1184914352, 1203999783, 1158167855, 1164975091, 1124077590, 
	    1188739475, 1192655580, 1173951661, 1127325140, 1180662882, 1130985203)
AND p.year>= 1980
;
-- QA
SELECT COUNT(1), COUNT(DISTINCT paperid) FROM top_aiconf_papers;

CREATE TEMP TABLE ai_fos_papers DISTKEY(paperid) SORTKEY(paperid) AS
select p.paperid,  p.doi,  p.paper_title, p.year, p.date,
	p.doc_type, p.conference_series_id, s.normalizedname conf_series, p.conference_instance_id, c.normalizedname conf_name,
    p.journal_id, j.normalizedname journal_name,
    p.citationcount, p.estimated_citation_count
from mag_ext.paperfieldsofstudy_pq pf
join 
    mag_ext.papers_pq p ON pf.paperid=p.paperid
LEFT JOIN 
    mag_ext.conferenceseries_pq s ON p.conference_series_id=s.conferenceseriesid
LEFT JOIN 
  mag_ext.conferenceinstances_pq c ON p.conference_instance_id=c.conferenceinstanceid
LEFT JOIN 
  mag_ext.journals_pq j ON p.journal_id=j.journalid
where pf.fieldofstudyid = 154945302
  and p.doc_type in ('Conference', 'Journal')
  and p.year>=1980
;
-- QA
SELECT COUNT(1), COUNT(DISTINCT paperid) FROM ai_fos_papers;

CREATE TEMP TABLE remove_overlap AS 
SELECT a.*
FROM ai_fos_papers a 
LEFT JOIN 
	top_aiconf_papers b ON a.paperid=b.paperid
WHERE b.paperid IS NULL
;

CREATE TABLE public.mag_ai_papers DISTKEY(paperid) SORTKEY(paperid) AS
SELECT * FROM top_aiconf_papers
UNION ALL
SELECT * FROM remove_overlap
;
GRANT SELECT ON public.mag_ai_papers TO johnconnor;

SELECT doc_type, COUNT(1) num_papers, avg(citationcount) avg_citations, avg(estimated_citation_count) avg_est_citations 
FROM public.mag_ai_papers 
GROUP BY 1;


--------------------------
-- Get author affiliations
--------------------------
CREATE TABLE public.mag_ai_paperauthors_country DISTKEY(paperid) SORTKEY(paperid) AS 
SELECT  
	  p.paperid, p.year,
      pa.authorsequencenumber, pa.authorid, a.normalizedname author_normalizedname,
      NVL(pa.affiliationid, a.lastknownaffiliationid) affiliationid, af.normalizedname as affiliation, NVL(gl.url, af.officialpage) affiliation_url, 
      af.Iso3166Code, g.country grid_country, 
      -- pu.languagecode,
      case when grid_country = 'United States' then 'US'
      when grid_country = 'China' then 'CN'
      when grid_country is not null and grid_country not in ('United States', 'China') then 'OT'
      when (officialpage LIKE '%.cn' or officialpage LIKE '%.cn/%') then 'CN'
      when (officialpage LIKE '%.hk' or officialpage LIKE '%.hk/%') then 'CN'
      -- when languagecode  = 'zh_chs' then 'CN'
      when Iso3166Code in ('US') then 'US'   
      when Iso3166Code in ('CN','HK') then 'CN'          
      when Iso3166Code is not null and Iso3166Code not in ('US','CN','HK') then 'OT'
      when (officialpage LIKE '%.com' or officialpage LIKE '%.com/%') then 'US'
      when (officialpage LIKE '%.edu' or officialpage LIKE '%.edu/%') then 'US'
      when (officialpage LIKE '%.org' or officialpage LIKE '%.org/%') then 'US'
      else 'OT' end country_code,
      case when lower(affiliation_url) like '%.com%' then 'com'
      when lower(affiliation_url) like '%.edu%' then 'edu' 
      when lower(affiliation_url) like '%.org%' then 'org' 
      else 'other' end domain_type     
FROM public.mag_ai_papers  p
LEFT JOIN 
    mag_ext.paperauthoraffiliations_pq pa ON p.paperid=pa.paperid
LEFT JOIN 
	mag_ext.authors_pq a ON pa.authorid=a.authorid    
LEFT JOIN 
    mag_ext.affiliations_pq af ON NVL(pa.affiliationid, a.lastknownaffiliationid)=af.affiliationid
LEFT JOIN 
	content.grid g ON af."grid id"=g.grid_id
LEFT JOIN 
	(select grid_id, max(link) as url from content.grid_links group by 1) gl ON g.grid_id=gl.grid_id
-- LEFT JOIN 
-- 	(select distinct "paper id" as paperid, LanguageCode from content_ext.mag_paperlanguages where LanguageCode = 'zh_chs') pu 
-- 	ON p.paperid=pu.paperid
;
GRANT SELECT ON public.mag_ai_paperauthors_country TO johnconnor;
