set names utf8;

ALTER TABLE dailyreport_engprofile ADD `inspector_name` varchar(128) DEFAULT NULL;
ALTER TABLE dailyreport_engprofile ADD `contractor_name` varchar(128) DEFAULT NULL;