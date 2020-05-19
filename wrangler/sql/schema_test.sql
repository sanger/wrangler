CREATE DATABASE IF NOT EXISTS `mlwarehouse_test` /*!40100 DEFAULT CHARACTER SET latin1 */;
DROP TABLE IF EXISTS `mlwarehouse_test`.`cgap_heron`;
/* The CREATE TABLE statement below needs to be on one line for the statement to execute properly using the mysql library - a possible issue to fix*/;
CREATE TABLE `mlwarehouse_test`.`cgap_heron` (`id` int(11) NOT NULL AUTO_INCREMENT,`container_barcode` varchar(255) NOT NULL,`tube_barcode` varchar(255),`supplier_sample_id` varchar(255) NOT NULL,`position` varchar(45) NOT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
