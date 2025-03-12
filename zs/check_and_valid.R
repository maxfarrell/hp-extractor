library(tidyverse)
library(knitr)
library(rmarkdown)

run <- "0312"
setwd(paste0("H:\\Working\\hp-extractor\\zs\\", run))

files <- list.files()
files

ent1 <- read.csv(paste0("entities_", run, "_prompt1.csv")) %>% select(-any_of(c("X", "entity_id"))) %>% separate_longer_delim(doc_ids, delim = ";") %>% rename(doc_id = doc_ids) %>% distinct
ent2 <- read.csv(paste0("entities_", run, "_prompt2.csv")) %>% select(-any_of(c("X", "entity_id"))) %>% separate_longer_delim(doc_ids, delim = ";") %>% rename(doc_id = doc_ids) %>% distinct
ent3 <- read.csv(paste0("entities_", run, "_prompt3.csv")) %>% select(-any_of(c("X", "entity_id"))) %>% separate_longer_delim(doc_ids, delim = ";") %>% rename(doc_id = doc_ids) %>% distinct
ent4 <- read.csv(paste0("entities_", run, "_prompt4.csv")) %>% select(-any_of(c("X", "entity_id"))) %>% separate_longer_delim(doc_ids, delim = ";") %>% rename(doc_id = doc_ids) %>% distinct
ent5 <- read.csv(paste0("entities_", run, "_prompt5.csv")) %>% select(-any_of(c("X", "entity_id"))) %>% separate_longer_delim(doc_ids, delim = ";") %>% rename(doc_id = doc_ids) %>% distinct

rel1 <- read.csv(paste0("relationships_", run, "_prompt1.csv")) %>% separate_longer_delim(doc_id, delim = ";")
rel2 <- read.csv(paste0("relationships_", run, "_prompt2.csv")) %>% separate_longer_delim(doc_id, delim = ";")
rel3 <- read.csv(paste0("relationships_", run, "_prompt3.csv")) %>% separate_longer_delim(doc_id, delim = ";")
rel4 <- read.csv(paste0("relationships_", run, "_prompt4.csv")) %>% separate_longer_delim(doc_id, delim = ";")
rel5 <- read.csv(paste0("relationships_", run, "_prompt5.csv")) %>% separate_longer_delim(doc_id, delim = ";")

meta <- read.table("H:\\Working\\system_specificity\\raw_data\\dat_march8_2021.tsv", sep = '\t', comment.char="", quote = "\"", header=TRUE) %>% distinct
meta_aug <- read.table("H:\\Working\\system_specificity\\raw_data\\dat_aug9_2021.tsv", sep = '\t', comment.char="", quote = "\"", header=TRUE) %>% distinct

meta %>% filter(ReferenceText == "Dubay et al 2006b")
meta_aug %>% filter(ReferenceText == "Dubay et al 2006b")

val <- read.csv("H:\\Working\\hp-extractor\\raw_data\\validation_100.csv")

meta %>% filter(pmid == 24023772) %>% pull(absID)
meta_aug %>% filter(pmid == 24023772) %>% pull(absID)

# Produce reader
ent1 %>%
  arrange(factor(doc_id, levels = val$absID)) %>%
  write.csv(paste0("entities_", run, "_prompt1_VALID.csv"))

rel1 %>%
  arrange(factor(doc_id, levels = val$absID)) %>%
  write.csv(paste0("relationships_", run, "_prompt1_VALID.csv"))

render("manual_validation_display.Rmd", output_file="manual_validation_display.html")


# # Should be docs 1 - 99
# 
ent1 %>% pull(doc_id) %>% unique %>% length
ent2 %>% pull(doc_id) %>% unique %>% length
ent3 %>% pull(doc_id) %>% unique %>% length
ent4 %>% pull(doc_id) %>% unique %>% length
ent5 %>% pull(doc_id) %>% unique %>% length
rel1 %>% pull(doc_id) %>% unique %>% length
rel2 %>% pull(doc_id) %>% unique %>% length
rel3 %>% pull(doc_id) %>% unique %>% length
rel4 %>% pull(doc_id) %>% unique %>% length
rel5 %>% pull(doc_id) %>% unique %>% length

e1x <- val %>% pull(absID) %>% .[!(. %in% ent1$doc_id)]
e2x <- val %>% pull(absID) %>% .[!(. %in% ent2$doc_id)]
e3x <- val %>% pull(absID) %>% .[!(. %in% ent3$doc_id)]
e4x <- val %>% pull(absID) %>% .[!(. %in% ent4$doc_id)]
e5x <- val %>% pull(absID) %>% .[!(. %in% ent5$doc_id)]
r1x <- val %>% pull(absID) %>% .[!(. %in% rel1$doc_id)]
r2x <- val %>% pull(absID) %>% .[!(. %in% rel2$doc_id)]
r3x <- val %>% pull(absID) %>% .[!(. %in% rel3$doc_id)]
r4x <- val %>% pull(absID) %>% .[!(. %in% rel4$doc_id)]
r5x <- val %>% pull(absID) %>% .[!(. %in% rel5$doc_id)]

g <- table(unique(stack(list(e1x = e1x, 
                             e2x = e2x,
                             e3x = e3x,
                             e4x = e4x,
                             e5x = e5x,
                             r1x = r1x,
                             r2x = r2x,
                             r3x = r3x,
                             r4x = r4x,
                             r5x = r5x)))) %>% as.data.frame.matrix

names(g) <- files[c(1:5,7:11)]

+(!g) %>% write.csv(paste0("missing_doc_ids_", run, ".csv"))

# Avg ents/rels per doc

ent1 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary
ent2 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary
ent3 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary
ent4 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary
ent5 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary
rel1 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary
rel2 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary
rel3 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary
rel4 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary
rel5 %>% group_by(doc_id) %>% tally %>% pull(n) %>% summary

# Set focal ent/rel prompt to check

fent <- ent1
frel <- rel1

# Types of ent/rel
fent %>% group_by(type) %>% tally() %>% arrange(-n)
fent %>% filter(!(doc_id %in% c(fent %>% filter(type == "Host") %>% pull(doc_id)))) # abs without "Host" ent
fent %>% filter(!(doc_id %in% c(fent %>% filter(type == "Pathogen") %>% pull(doc_id)))) # abs without "Pathogen" ent

frel %>% group_by(relation_type) %>% tally() %>% arrange(-n)
frel %>% filter(!(doc_id %in% c(frel %>% filter(relation_type == "hosts") %>% pull(doc_id)))) # abs without "hosts" rel
frel %>% filter(!(doc_id %in% c(frel %>% filter(relation_type == "infects") %>% pull(doc_id)))) # abs without "infects" rel

frel %>% filter(relation_type == "hosts") # view hosts relations
frel %>% filter(relation_type == "infects") # view infects relations

# Find entities in source/target but not extracted in the entity file
missing_source <- lapply(val$absID, function(i)
  frel %>% filter(doc_id == i & !(source_text %in% (fent %>% filter(doc_id == i) %>% pull(entity))))
) %>%
  bind_rows

missing_source %>% pull(doc_id) %>% unique %>% length

missing_target <- lapply(val$absID, function(i)
  frel %>% filter(doc_id == i & !(target_text %in% (fent %>% filter(doc_id == i) %>% pull(entity))))
) %>%
  bind_rows

missing_target %>% pull(doc_id) %>% unique %>% length

# Latin names/common names
fent %>% filter(type == "Host") # view Host entities
fent %>% filter(type == "Pathogen") # view Pathogen entities
fent %>% filter(type == "Common name") # view Common name entities

frel %>% filter(relation_type == "common name of") # View synonym relations
frel %>% filter(relation_type == "latin name of") # View synonym relations
fent %>% filter(type == "Common name" & doc_id %in% (frel %>% filter(relation_type == "common name of") %>% pull(doc_id)))

frel %>% filter(doc_id == 85)
fent %>% filter(doc_id == 85)


val %>% filter(doc_id == 85)

