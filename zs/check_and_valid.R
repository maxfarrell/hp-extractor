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

# Check canon H-P from CLOVER

val %>% left_join(meta_aug) %>% select(absID, Host, HostOriginal, Host_AsReported, Pathogen, PathogenOriginal, Pathogen_AsReported) %>% write.csv("valid_hp_canon.csv")


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





### Compare different models

run <- "0331"
setwd(paste0("H:\\Working\\hp-extractor\\zs\\", run))

files <- list.files()
files

ent_d <- read.csv("entities_0327_no_merge_single_id_deepseek-r1-distill-qwen-32b.csv")%>% distinct
ent_g <- read.csv("entities_0327_no_merge_single_id_gemma2.csv") %>% distinct
ent_l <- read.csv("entities_0327_no_merge_single_id_llama.csv") %>% distinct
ent_m <- read.csv("entities_0327_no_merge_single_id_mistral.csv") %>% distinct

rel_d <- read.csv("relationships_0327_no_merge_single_id_deepseek-r1-distill-qwen-32b.csv") %>% distinct
rel_g <- read.csv("relationships_0327_no_merge_single_id_gemma2.csv") %>% distinct
rel_l <- read.csv("relationships_0327_no_merge_single_id_llama.csv") %>% distinct
rel_m <- read.csv("relationships_0327_no_merge_single_id_mistral.csv") %>% distinct

meta_aug <- read.table("H:\\Working\\system_specificity\\raw_data\\dat_aug9_2021.tsv", sep = '\t', comment.char="", quote = "\"", header=TRUE) %>% distinct

val <- read.csv("H:\\Working\\hp-extractor\\raw_data\\validation_100.csv")


# Should be docs 1 - 100
ent_d %>% pull(doc_id) %>% unique %>% length
ent_g %>% pull(doc_id) %>% unique %>% length
ent_l %>% pull(doc_id) %>% unique %>% length
ent_m %>% pull(doc_id) %>% unique %>% length
rel_d %>% pull(doc_id) %>% unique %>% length
rel_g %>% pull(doc_id) %>% unique %>% length
rel_l %>% pull(doc_id) %>% unique %>% length
rel_m %>% pull(doc_id) %>% unique %>% length

# Avg ents/rels per doc
bind_rows(
ent_d %>% group_by(doc_id) %>% tally %>% mutate(model = "deepseek"),
ent_g %>% group_by(doc_id) %>% tally %>% mutate(model = "gemma2"),
ent_l %>% group_by(doc_id) %>% tally %>% mutate(model = "llama"),
ent_m %>% group_by(doc_id) %>% tally %>% mutate(model = "mistral"),
) %>%
  ggplot(aes(x=n, fill=model)) +
  geom_density(alpha=0.2, position = 'identity') +
  xlab("entities per abstract") +
  theme_bw()
  

bind_rows(
  rel_d %>% group_by(doc_id) %>% tally %>% mutate(model = "deepseek"),
  rel_g %>% group_by(doc_id) %>% tally %>% mutate(model = "gemma2"),
  rel_l %>% group_by(doc_id) %>% tally %>% mutate(model = "llama"),
  rel_m %>% group_by(doc_id) %>% tally %>% mutate(model = "mistral"),
) %>%
  ggplot(aes(x=n, fill=model)) +
  geom_density(alpha=0.2, position = 'identity') +
  xlab("relations per abstract") +
  theme_bw()


# Types of ent/rel
plot_lev_ent <- bind_rows(
  ent_d %>% group_by(type) %>% tally %>% mutate(model = "deepseek"),
  ent_g %>% group_by(type) %>% tally %>% mutate(model = "gemma2"),
  ent_l %>% group_by(type) %>% tally %>% mutate(model = "llama"),
  ent_m %>% group_by(type) %>% tally %>% mutate(model = "mistral"),
) %>% filter(n>25) %>% select(-model) %>% group_by(type) %>% summarise(ov = sum(n)) %>% arrange(ov) %>% pull(type)

bind_rows(
  ent_d %>% group_by(type) %>% tally %>% mutate(model = "deepseek"),
  ent_g %>% group_by(type) %>% tally %>% mutate(model = "gemma2"),
  ent_l %>% group_by(type) %>% tally %>% mutate(model = "llama"),
  ent_m %>% group_by(type) %>% tally %>% mutate(model = "mistral"),
) %>%
  filter(n > 50) %>%
  ggplot(aes(y=factor(type, levels = plot_lev_ent), x=n,color=model)) +
  geom_point(size = 5) +
  ylab("entity type (min = 50)") +
  theme_bw()

plot_lev_rel <- bind_rows(
  rel_d %>% group_by(relation_type) %>% tally %>% mutate(model = "deepseek"),
  rel_g %>% group_by(relation_type) %>% tally %>% mutate(model = "gemma2"),
  rel_l %>% group_by(relation_type) %>% tally %>% mutate(model = "llama"),
  rel_m %>% group_by(relation_type) %>% tally %>% mutate(model = "mistral"),
) %>% filter(n>25) %>% select(-model) %>% group_by(relation_type) %>% summarise(ov = sum(n)) %>% arrange(ov) %>% pull(relation_type)

bind_rows(
  rel_d %>% group_by(relation_type) %>% tally %>% mutate(model = "deepseek"),
  rel_g %>% group_by(relation_type) %>% tally %>% mutate(model = "gemma2"),
  rel_l %>% group_by(relation_type) %>% tally %>% mutate(model = "llama"),
  rel_m %>% group_by(relation_type) %>% tally %>% mutate(model = "mistral"),
) %>%
  filter(n > 25) %>%
  ggplot(aes(y=factor(relation_type, levels = plot_lev_rel), x=n,color=model)) +
  geom_point(size = 5) +
  ylab("relation type (min = 20)") +
  theme_bw()


ent_d %>% filter(!(doc_id %in% c(ent_d %>% filter(type == "Host") %>% pull(doc_id)))) # abs without "Host" ent
ent_g %>% filter(!(doc_id %in% c(ent_g %>% filter(type == "Host") %>% pull(doc_id)))) # abs without "Host" ent
ent_l %>% filter(!(doc_id %in% c(ent_l %>% filter(type == "Host") %>% pull(doc_id)))) # abs without "Host" ent
ent_m %>% filter(!(doc_id %in% c(ent_m %>% filter(type == "Host") %>% pull(doc_id)))) # abs without "Host" ent

ent_d %>% filter(!(doc_id %in% c(ent_d %>% filter(type == "Pathogen") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without "Pathogen" ent
ent_g %>% filter(!(doc_id %in% c(ent_g %>% filter(type == "Pathogen") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without "Pathogen" ent
ent_l %>% filter(!(doc_id %in% c(ent_l %>% filter(type == "Pathogen") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without "Pathogen" ent
ent_m %>% filter(!(doc_id %in% c(ent_m %>% filter(type == "Pathogen") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without "Pathogen" ent


rel_d %>% filter(!(doc_id %in% c(rel_d %>% filter(relation_type == "hosts") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length  # abs without "hosts" rel
rel_g %>% filter(!(doc_id %in% c(rel_g %>% filter(relation_type == "hosts") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length  # abs without "hosts" rel
rel_l %>% filter(!(doc_id %in% c(rel_l %>% filter(relation_type == "hosts") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length  # abs without "hosts" rel
rel_m %>% filter(!(doc_id %in% c(rel_m %>% filter(relation_type == "hosts") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length  # abs without "hosts" rel

rel_d %>% filter(!(doc_id %in% c(rel_d %>% filter(relation_type == "infects") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without "infects" rel
rel_g %>% filter(!(doc_id %in% c(rel_g %>% filter(relation_type == "infects") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without "infects" rel
rel_l %>% filter(!(doc_id %in% c(rel_l %>% filter(relation_type == "infects") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without "infects" rel
rel_m %>% filter(!(doc_id %in% c(rel_m %>% filter(relation_type == "infects") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without "infects" rel

rel_d %>% filter(!(doc_id %in% c(rel_d %>% filter(relation_type == "infects"|relation_type == "hosts") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without either
rel_g %>% filter(!(doc_id %in% c(rel_g %>% filter(relation_type == "infects"|relation_type == "hosts") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without either
rel_l %>% filter(!(doc_id %in% c(rel_l %>% filter(relation_type == "infects"|relation_type == "hosts") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without either
rel_m %>% filter(!(doc_id %in% c(rel_m %>% filter(relation_type == "infects"|relation_type == "hosts") %>% pull(doc_id)))) %>% pull(doc_id) %>% unique %>% length # abs without either

# Find entities in source/target but not extracted in the entity file
missing_source_d <- lapply(val$absID, function(i) rel_d %>% filter(doc_id == i & !(tolower(source_text) %in% (ent_d %>% filter(doc_id == i) %>% mutate(entity = tolower(entity)) %>% pull(entity))))) %>%  bind_rows
missing_source_g <- lapply(val$absID, function(i) rel_g %>% filter(doc_id == i & !(tolower(source_text) %in% (ent_g %>% filter(doc_id == i) %>% mutate(entity = tolower(entity)) %>% pull(entity))))) %>%  bind_rows
missing_source_l <- lapply(val$absID, function(i) rel_l %>% filter(doc_id == i & !(tolower(source_text) %in% (ent_l %>% filter(doc_id == i) %>% mutate(entity = tolower(entity)) %>% pull(entity))))) %>%  bind_rows
missing_source_m <- lapply(val$absID, function(i) rel_m %>% filter(doc_id == i & !(tolower(source_text) %in% (ent_m %>% filter(doc_id == i) %>% mutate(entity = tolower(entity)) %>% pull(entity))))) %>%  bind_rows

missing_source_d %>% pull(doc_id) %>% unique %>% length
missing_source_g %>% pull(doc_id) %>% unique %>% length
missing_source_l %>% pull(doc_id) %>% unique %>% length
missing_source_m %>% pull(doc_id) %>% unique %>% length

missing_target_d <- lapply(val$absID, function(i) rel_d %>% filter(doc_id == i & !(tolower(target_text) %in% (ent_d %>% filter(doc_id == i) %>% mutate(entity = tolower(entity)) %>% pull(entity))))) %>%  bind_rows
missing_target_g <- lapply(val$absID, function(i) rel_g %>% filter(doc_id == i & !(tolower(target_text) %in% (ent_g %>% filter(doc_id == i) %>% mutate(entity = tolower(entity)) %>% pull(entity))))) %>%  bind_rows
missing_target_l <- lapply(val$absID, function(i) rel_l %>% filter(doc_id == i & !(tolower(target_text) %in% (ent_l %>% filter(doc_id == i) %>% mutate(entity = tolower(entity)) %>% pull(entity))))) %>%  bind_rows
missing_target_m <- lapply(val$absID, function(i) rel_m %>% filter(doc_id == i & !(tolower(target_text) %in% (ent_m %>% filter(doc_id == i) %>% mutate(entity = tolower(entity)) %>% pull(entity))))) %>%  bind_rows

missing_target_d %>% pull(doc_id) %>% unique %>% length
missing_target_g %>% pull(doc_id) %>% unique %>% length
missing_target_l %>% pull(doc_id) %>% unique %>% length
missing_target_m %>% pull(doc_id) %>% unique %>% length


# Latin names/common names
ent_d %>% filter(type == "Common name") # view Common name entities
ent_g %>% filter(type == "Common name") # view Common name entities
ent_l %>% filter(type == "Common name") # view Common name entities
ent_m %>% filter(type == "Common name") # view Common name entities

rel_d %>% filter(relation_type == "common name of") # View synonym relations
rel_d %>% filter(relation_type == "latin name of") # View synonym relations

rel_g %>% filter(relation_type == "common name of") # View synonym relations
rel_g %>% filter(relation_type == "latin name of") # View synonym relations

rel_l %>% filter(relation_type == "common name of") # View synonym relations
rel_l %>% filter(relation_type == "latin name of") # View synonym relations

rel_m %>% filter(relation_type == "common name of") # View synonym relations
rel_m %>% filter(relation_type == "latin name of") # View synonym relations

