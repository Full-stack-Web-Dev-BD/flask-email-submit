-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Feb 22, 2025 at 05:03 PM
-- Wersja serwera: 5.7.40-log
-- Wersja PHP: 8.3.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fastcnc_db`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `wp_lsr_opts_materials`
--

CREATE TABLE `wp_lsr_opts_materials` (
  `id` smallint(5) UNSIGNED NOT NULL,
  `material` tinytext COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `thickness` decimal(6,1) NOT NULL,
  `setup_price` decimal(6,3) DEFAULT '0.000',
  `cost_factor` decimal(6,3) DEFAULT '1.000',
  `loop_cost` decimal(6,3) DEFAULT '0.000',
  `cost_per_m2` decimal(6,3) DEFAULT '0.000',
  `in_stock` tinyint(1) DEFAULT '1',
  `index` smallint(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

--
-- Dumping data for table `wp_lsr_opts_materials`
--

INSERT INTO `wp_lsr_opts_materials` (`id`, `material`, `thickness`, `setup_price`, `cost_factor`, `loop_cost`, `cost_per_m2`, `in_stock`, `index`) VALUES
(4, 'Steel DC01 / 1.0330', 1.0, 4.200, 0.935, 0.090, 10.560, 1, 26),
(5, 'Steel DC01 / 1.0330', 1.2, 4.200, 0.935, 0.090, 13.200, 1, 25),
(6, 'Steel DC01 / 1.0330', 1.5, 4.200, 0.935, 0.090, 16.450, 1, 24),
(7, 'Steel DC01 / 1.0330', 2.0, 4.200, 0.935, 0.090, 18.300, 1, 23),
(8, 'Steel DC01 / 1.0330', 3.0, 4.200, 0.935, 0.090, 34.250, 1, 22),
(9, 'Steel S235 / 1.0038', 4.0, 3.900, 0.998, 0.098, 32.000, 1, 21),
(10, 'Steel S235 / 1.0038', 5.0, 3.900, 0.932, 0.098, 38.230, 1, 20),
(11, 'Steel S235 / 1.0038', 6.0, 3.900, 0.932, 0.098, 41.958, 1, 19),
(12, 'Steel S235 / 1.0038', 8.0, 3.900, 0.979, 0.111, 51.040, 0, 18),
(13, 'Steel S235 / 1.0038', 10.0, 4.500, 1.110, 0.128, 66.200, 1, 17),
(14, 'Steel S235 / 1.0038', 12.0, 4.600, 1.300, 0.167, 81.580, 0, 16),
(15, 'Stainless Steel AISI 304 / 1.4301', 0.5, 5.200, 0.582, 0.081, 19.000, 1, 15),
(16, 'Stainless Steel AISI 304 / 1.4301', 0.8, 5.200, 0.583, 0.082, 21.920, 0, 14),
(17, 'Stainless Steel AISI 304 / 1.4301', 1.0, 5.200, 0.629, 0.083, 26.600, 1, 13),
(18, 'Stainless Steel AISI 304 / 1.4301', 1.2, 3.300, 0.655, 0.084, 31.800, 1, 12),
(19, 'Stainless Steel AISI 304 / 1.4301', 1.5, 5.200, 0.722, 0.090, 38.460, 0, 11),
(20, 'Stainless Steel AISI 304 / 1.4301', 2.0, 5.200, 0.804, 0.110, 51.280, 1, 10),
(21, 'Stainless Steel AISI 304 / 1.4301', 2.5, 5.200, 0.885, 0.120, 65.500, 0, 9),
(22, 'Stainless Steel AISI 304 / 1.4301', 3.0, 5.200, 0.967, 0.135, 77.150, 1, 8),
(23, 'Stainless Steel AISI 304 / 1.4301', 4.0, 5.200, 1.130, 0.163, 102.790, 1, 7),
(24, 'Stainless Steel AISI 304 / 1.4301', 5.0, 5.200, 1.328, 0.186, 149.000, 1, 6),
(25, 'Stainless Steel AISI 304 / 1.4301', 6.0, 5.200, 1.608, 0.221, 198.000, 1, 5),
(26, 'Aluminum 5754 / Al-Mg3 / 3.3535', 1.0, 5.200, 0.582, 0.070, 9.790, 1, 4),
(27, 'Aluminum 5754 / Al-Mg3 / 3.3535', 2.0, 5.200, 0.804, 0.076, 18.880, 1, 3),
(28, 'Aluminum 5754 / Al-Mg3 / 3.3535', 3.0, 5.200, 0.967, 0.097, 29.830, 1, 2),
(29, 'Aluminum 5754 / Al-Mg3 / 3.3535', 4.0, 5.200, 1.156, 0.110, 39.700, 1, 1);

--
-- Indeksy dla zrzutów tabel
--

--
-- Indeksy dla tabeli `wp_lsr_opts_materials`
--
ALTER TABLE `wp_lsr_opts_materials`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `wp_lsr_opts_materials`
--
ALTER TABLE `wp_lsr_opts_materials`
  MODIFY `id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
