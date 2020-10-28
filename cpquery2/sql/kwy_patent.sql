-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- 主机： localhost
-- 生成日期： 2020-10-28 09:47:07
-- 服务器版本： 5.7.26
-- PHP 版本： 7.3.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `kwy`
--

-- --------------------------------------------------------

--
-- 表的结构 `kwy_patent`
--

CREATE TABLE `kwy_patent` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL DEFAULT '0' COMMENT '用户id',
  `patent_no` varchar(50) NOT NULL DEFAULT '' COMMENT '专利号',
  `patent_name` varchar(255) NOT NULL DEFAULT '' COMMENT '专利名称',
  `patent_type` tinyint(4) NOT NULL DEFAULT '1' COMMENT '专利类型，1：发明,2:实用新型，3：外观设计',
  `applicant` varchar(255) NOT NULL DEFAULT '' COMMENT '专利权人',
  `address` varchar(255) NOT NULL DEFAULT '' COMMENT '地址',
  `inventor` varchar(255) NOT NULL DEFAULT '' COMMENT '发明人或设计人',
  `ipc` varchar(50) NOT NULL DEFAULT '' COMMENT '主分类号',
  `applicant_date` date NOT NULL DEFAULT '0000-00-00' COMMENT '申报日期',
  `publication_no` varchar(50) NOT NULL DEFAULT '' COMMENT '公告号',
  `publication_date` date NOT NULL DEFAULT '0000-00-00' COMMENT '公告日期',
  `auth_publication_date` date NOT NULL DEFAULT '0000-00-00' COMMENT '授权公告日期',
  `description` text COMMENT '摘要',
  `status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '专利状态，默认0，其他记录值，参考专利模块',
  `status_updated_time` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `first_agency` varchar(255) NOT NULL DEFAULT '' COMMENT '原代理机构',
  `agency_id` int(11) NOT NULL DEFAULT '0' COMMENT 'patent_agency表ID',
  `is_core` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否核心专利，1：核心',
  `is_sale` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否可售，1：可售',
  `annual_fee_limit_date` date NOT NULL DEFAULT '0000-00-00' COMMENT '年费缴纳限期',
  `is_notice` tinyint(4) NOT NULL DEFAULT '1' COMMENT '本年度年费缴纳是否自动通知，1：通知，0：不通知',
  `notice_type` varchar(10) NOT NULL DEFAULT '1' COMMENT '通知方式，1：到期前1个月，2：到期前1个星期，3：到期当天 ；多种方式，用逗号分割',
  `annual_fee_reduction` int(4) NOT NULL DEFAULT '0' COMMENT '费用减免比例',
  `created_id` int(11) NOT NULL DEFAULT '0',
  `created_time` datetime NOT NULL DEFAULT '0000-00-00 00:00:00'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- 转储表的索引
--

--
-- 表的索引 `kwy_patent`
--
ALTER TABLE `kwy_patent`
  ADD PRIMARY KEY (`id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `kwy_patent`
--
ALTER TABLE `kwy_patent`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
