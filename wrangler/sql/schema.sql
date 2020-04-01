CREATE DATABASE IF NOT EXISTS `mlwarehouse_test` /*!40100 DEFAULT CHARACTER SET latin1 */;
DROP TABLE IF EXISTS `heron`;
CREATE TABLE `heron` (`id` int(11) NOT NULL AUTO_INCREMENT,`tube_rack_barcode` varchar(255) NOT NULL,`tube_barcode` varchar(255) NOT NULL,`supplier_sample_id` varchar(255) NOT NULL,`position` varchar(45) NOT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
