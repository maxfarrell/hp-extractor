library(tidyverse)
library(magrittr)
library(stringr)

dat <- read.delim("raw_data/hp_metadata.tsv", sep="\t")
abst <- read.delim("raw_data/hp_abstracts.tsv", sep="\t", quote = "")

train <- read.csv("raw_data/prompt_design_absIDs.csv") %>% 
  left_join(dat %>% select(Host, Parasite, absID) %>% distinct) %>%
  mutate(Parasite = replace_na(Parasite, "Parapoxvirus"))

# Prompt 0

p0 <- read.csv("prompt_output/prompt0_results/prompt0.csv") %>% 
  mutate(Host = tolower(Host),
         Pathogen = tolower(Pathogen))

# For each true H-P association in train, calc precision by simple text matching
train %>%
  rowwise() %>%
  mutate(match = any(
   # str_detect(p0$absID, fixed(absID)) &
      str_detect(p0$Host, fixed(Host)) & 
      str_detect(p0$Pathogen, fixed(Parasite)))) %>%
  with(., table(match)) %>%
  prop.table() %>%
  .[2] %>%
  round(3)