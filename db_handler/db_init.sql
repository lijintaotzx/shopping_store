CREATE DATABASE shopping_store;

USE shopping_store;

CREATE TABLE `user` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(16) NOT NULL DEFAULT '',
  `pn` varchar(32) NOT NULL DEFAULT '',
  `role` int(11) DEFAULT '0',
  `password` varchar(500) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;

CREATE TABLE `product` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '',
  `description` varchar(64) DEFAULT NULL,
  `source_price` decimal(10,2) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `count` int(11) NOT NULL,
  `is_del` tinyint(1) NOT NULL DEFAULT '0',
  `order_id` varchar(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  INDEX(order_id),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE  TABLE order_record( user_id INT,
                         profit DECIMAL(10,2),
                         order_id   VARCHAR(64),
                          create_time datetime DEFAULT now(),
                          INDEX(order_id)
                          );

CREATE  TABLE order_detail(
    order_record_id INT,
    product_id INT,price DECIMAL(10,2),
    profit DECIMAL(10,2)
);

delimiter $$
create function st1() returns int
begin
return (select id from user order by id desc limit 1);
end $$
delimiter ;

delimiter $$
create procedure st2()
begin
select name from user;
select pn from user;
end $$

delimiter ;

delimiter $$
create procedure func1(out, id1, id2)
begin

