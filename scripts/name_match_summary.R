# name_match_summary.R

require(dplyr)

dat <- read.delim("../raw_data/hp_metadata.tsv", sep="\t", fileEncoding="UTF-8")
abst <- read.delim("../raw_data/hp_abstracts.tsv", sep="\t", quote = "", fileEncoding="UTF-8")

names(abst) <- c("abs","absID")

# remove start and end quotes for abstracts
abst$abs <- gsub("^[\"]","",abst$abs)
abst$abs <- gsub("[\"]$","",abst$abs)

# some titles are non-unique across unique abstracts
titles <- dat %>% select(absID, title) %>% unique()
titles <- titles[!is.na(titles$title),]
titles <- unique(titles)

sum(duplicated(titles$absID))
#2 titles duplicated

dup_titles <- titles$absID[duplicated(titles$absID)]
dat[dat$absID%in%dup_titles,] %>% unique()
# one is issue with capitalization in EID titles (same abstract, but titles from different PMIDs)
# other is issue with hp3 title as reference, but the true title exists in other databases

# going to leave these for now, but must return to fix this issue when expanding to run
# extraction over the entire database. 


# parasites
paras <- left_join(select(dat, PathogenOriginal, absID), abst) %>% unique()

# View(paras[is.na(paras$PathogenOriginal),])

# identify abstracs with missing metadata 
missing <- paras$absID[is.na(paras$PathogenOriginal)]
# missing # none

paras <- paras %>% 
  rowwise() %>% 
  mutate(verbatim = if_else(any(grepl(PathogenOriginal, abs, ignore.case=TRUE)), "Yes", "No"))

sum(paras$verbatim=="Yes")# 52,945
sum(paras$verbatim=="Yes")/nrow(paras)# 68% of pathogen-abstract combinations have verbatim mentions

length(unique(paras$absID[paras$verbatim=="Yes"]))# 43,980 abstracts


# hosts
hosts <- left_join(select(dat, Host, HostOriginal, absID), abst) %>% unique()

# if HostOriginal is missing, swap in cleaned host name
hosts$HostName <- hosts$HostOriginal
hosts$HostName[is.na(hosts$HostName)] <- hosts$Host[is.na(hosts$HostName)] 

# identify abstracts with missing metadata 
missing <- hosts$absID[is.na(hosts$HostName)]
# missing # none

hosts <- select(hosts, HostName, absID, abs) %>% unique()

hosts <- hosts %>% 
  rowwise() %>% 
  mutate(verbatim = if_else(any(grepl(HostName, abs, ignore.case=TRUE)), "Yes", "No"))

sum(hosts$verbatim=="Yes")# 6341
sum(hosts$verbatim=="Yes")/nrow(hosts)# 8.2% of host-abstract combinations have verbatim mentions

length(unique(hosts$absID[hosts$verbatim=="Yes"]))# 5,051

# View(hosts[hosts$verbatim=="Yes",])

# View(hosts[hosts$verbatim=="No",])
# hosts$HostName[hosts$verbatim=="No"] %>% tolower() %>% sort() %>% unique() %>% View()

# hosts$HostName[hosts$verbatim=="No"] %>% tolower() %>% table() %>% sort() %>% rev() %>% View()

verb_host_absIDs <- hosts$absID[hosts$verbatim=="Yes"]
verb_para_absIDs <- paras$absID[hosts$verbatim=="Yes"]

abs_with_verbatim_sp <- data.frame(sort(intersect(verb_host_absIDs,verb_para_absIDs)))
names(abs_with_verbatim_sp) <- "absID"

abs_with_verbatim_sp

write.csv(abs_with_verbatim_sp, "../raw_data/abs_with_verbatim_names.csv", row.names=F)


# subset to exclude EID2 abstracts
eid2 <- dat[dat$Database%in%"EID2",]

abs_with_verbatim_noEID2 <- setdiff(abs_with_verbatim_sp$absID, eid2$absID)
length(abs_with_verbatim_noEID2)#492

dat_noeid <- dat[!dat$absID%in%eid2$absID,]

dat_test <- dat_noeid[dat_noeid$absID%in%abs_with_verbatim_noEID2,]

dat_test$PathogenType[dat_test$PathogenType=="Virus"] <- "virus"
dat_test$PathogenType[dat_test$PathogenType=="Bacteria"] <- "bacteria"

dat_test %>% group_by(PathogenType) %>% summarise(n_abs=n_distinct(absID))

set.seed(10927235)

n_hps <- dat_test
n_hps$hp <- paste(n_hps$HostName, n_hps$PathogenOriginal)
n_hps <- n_hps %>% group_by(absID) %>% summarise(n_hps=n_distinct(hp))
n_hps$single_multi <- NA
n_hps$single_multi[n_hps$n_hps==1] <- "single"
n_hps$single_multi[n_hps$n_hps>1] <- "multi"

dat_test <- left_join(dat_test, n_hps)

set.seed(10927235)
validation_set <- dat_test %>% filter(!is.na(PathogenType)) %>% 
					group_by(PathogenType, single_multi) %>%
					select(absID, PathogenType) %>% 
					distinct() %>% sample_n(13) %>% 
					ungroup() %>% unique() 

n_distinct(validation_set$absID)
dim(validation_set)

validation_set_absID <- select(validation_set, c(single_multi, absID)) %>% unique()
n_distinct(validation_set_absID$absID)

write.csv(validation_set_absID, "../raw_data/validation_set_absIDs.csv", row.names=F)


# writing title + abstracts for validation set to file
validation_100_title_abs <- left_join(validation_set_absID, abst)
validation_100_title_abs <- left_join(validation_100_title_abs, dat %>% select(absID, title))

# removing absID titles which are NA if there is an existing title available
validation_100_title_abs <- validation_100_title_abs %>% group_by(absID) %>% 
								mutate(n_titles=n_distinct(title)) 

validation_100_title_abs <- validation_100_title_abs %>% filter(!(n_titles>1 & is.na(title))) %>% select(-n_titles)

# merging titles and abstracts
validation_100_title_abs <- validation_100_title_abs %>% 
								tidyr::unite(., col = "title_abs",  title, abs, na.rm=TRUE, sep = " ") %>%
								unique()

write.csv(validation_100_title_abs, "../raw_data/validation_100.csv", row.names=F)


# validation_set$PathogenType %>% table()
# validation_set$single_multi %>% table()
					
# View(validation_set)

# validation_set_dat <- left_join(validation_set, dat_test)

# names(validation_set_dat)
# dim(validation_set_dat)
# validation_set_dat %>% select(-c(AssocID)) %>% unique() %>% dim()


# prompt_set <- dat_test %>% filter(!is.na(PathogenType)) %>% 
# 						group_by(PathogenType) %>% 
# 						select(absID, PathogenType) %>% 
# 						distinct() %>% sample_n(10) %>% 
# 						ungroup() %>% select(absID) %>%  unique() 

# names(prompt_set) <- "absID"

# test_set <- data.frame(setdiff(dat_test$absID, prompt_set$absID))
# names(test_set) <- "absID"

# write.csv(prompt_set, "../raw_data/prompt_design_absIDs.csv", row.names=F)
# write.csv(test_set, "../raw_data/test_set_absIDs.csv", row.names=F)
