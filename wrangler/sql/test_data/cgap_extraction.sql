-- Rack to be wrangled
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'RACK-1','ABC101','Sample1','A1', 'Lysate', 'heron', 'CGAP Extraction', null, 1);
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'RACK-1','ABC102','Sample2','B1', 'Lysate', 'heron', 'CGAP Extraction', null, 1);
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'RACK-1','ABC103','Sample3','C1', 'Lysate', 'heron', 'CGAP Extraction', null, 1);
-- Plate to be wrangled
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'PLTE-1',null,'Sample4','A1', 'Lysate', 'heron r and d', 'CGAP Extraction', null, 1);
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'PLTE-1',null,'Sample5','B1', 'Lysate', 'heron r and d', 'CGAP Extraction', null, 1);
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'PLTE-1',null,'Sample6','C1', 'Lysate', 'heron r and d', 'CGAP Extraction', null, 1);
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'PLTE-1',null,'Sample7','D1', 'Lysate', 'heron r and d', 'CGAP Extraction', null, 1);
-- Wrangled Rack
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'RACK-2','ABC104','Sample8','A1', 'Lysate', 'heron', 'CGAP Extraction', NOW(), 1);
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'RACK-2','ABC105','Sample9','B1', 'Lysate', 'heron', 'CGAP Extraction', NOW(), 1);
INSERT INTO `{{ database }}`.`cgap_heron` VALUES (null,'RACK-2','ABC106','Sample10','C1', 'Lysate', 'heron', 'CGAP Extraction', NOW(), 1);