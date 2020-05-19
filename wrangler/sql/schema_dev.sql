CREATE DATABASE IF NOT EXISTS `mlwarehouse_dev` /*!40100 DEFAULT CHARACTER SET latin1 */;
DROP TABLE IF EXISTS `mlwarehouse_dev`.`cgap_heron`;
CREATE TABLE `mlwarehouse_dev`.`cgap_heron` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `container_barcode` VARCHAR(255) NOT NULL,
    `tube_barcode` VARCHAR(255),
    `supplier_sample_id` VARCHAR(255) NOT NULL,
    `position` VARCHAR(45) NOT NULL,
    PRIMARY KEY (`id`)
)  ENGINE=INNODB AUTO_INCREMENT=1 DEFAULT CHARSET=LATIN1;
