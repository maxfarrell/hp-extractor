# name_match_summary.R

require(dplyr)

dat <- read.delim("../raw_data/hp_metadata.tsv", sep="\t")
abst <- read.delim("../raw_data/hp_abstracts.tsv", sep="\t", quote = "")

names(dat)
names(abst) <- c("abs","absID")

host_tax <- read.csv("../raw_data/hosts_highertax_manualcheck_r.csv")
host_tax$Host <- tolower(host_tax$Host)

dat <- left_join(dat, host_tax)

dat$PathogenType[dat$PathogenType=="Virus"] <- "virus"

dat %>% group_by(PathogenType) %>% summarise(n_abs = n_distinct(absID)) %>% arrange(n_abs)

viruses <- dat %>% group_by(PathogenType) %>% filter(PathogenType=="virus")

viruses %>% group_by(Database) %>% summarise(n_abs = n_distinct(absID))

secs <- (17500 * 5)
mins <- secs/60
hours <- mins/60
days <- hours/24
days/4

names(dat)

# viruses %>% group_by(HostClass) %>% summarise(n_abs = n_distinct(absID))


# keep only viruses and merge title and abstracts together
viruses <- left_join(viruses, abst)
viruses$title_abs <- paste(viruses$title, viruses$abs, sep=" ")

# title_abs <- viruses %>% ungroup %>% select(absID, title_abs) %>% unique()

virus_absID <- viruses %>% ungroup() %>% select(absID) %>% unique()

write.csv(virus_absID, "../raw_data/virus_abstracts.csv", row.names=F)



# parasites
paras <- left_join(select(dat, PathogenOriginal, absID), abst) %>% unique()

# View(paras[is.na(paras$PathogenOriginal),])

# identify abstracs with missing metadata 
missing <- paras$absID[is.na(paras$PathogenOriginal)]

# remove abstracts with NA for parasite name
paras <- paras[!is.na(paras$PathogenOriginal),]

length(missing)
length(intersect(paras$absID, missing))
# View(paras[paras$absID %in% missing,])
# these missing absID are represented with metadata... go back to original data and clean this.

paras <- paras %>% 
  rowwise() %>% 
  mutate(verbatim = if_else(any(grepl(PathogenOriginal, abs, ignore.case=TRUE)), "Yes", "No"))

sum(paras$verbatim=="Yes")# 52,945
sum(paras$verbatim=="Yes")/nrow(paras)# 68% of pathogen-abstract combinations have verbatim mentions

length(unique(paras$absID[paras$verbatim=="Yes"]))# 43,980 abstracts


# hosts
hosts <- left_join(select(dat, Host, HostOriginal, absID), abst) %>% unique()

# if HostOriginal is missing, swap in host name
hosts$HostName <- hosts$HostOriginal
hosts$HostName[is.na(hosts$HostName)] <- hosts$Host[is.na(hosts$HostName)] 

# identify abstracts with missing metadata 
missing <- hosts$absID[is.na(hosts$HostName)]

# remove abstracts with NA for Host name
hosts <- hosts[!is.na(hosts$HostName),]

length(missing)
length(intersect(hosts$absID, missing))

hosts <- select(hosts, HostName, absID, abs) %>% unique()

hosts <- hosts %>% 
  rowwise() %>% 
  mutate(verbatim = if_else(any(grepl(HostName, abs, ignore.case=TRUE)), "Yes", "No"))

sum(hosts$verbatim=="Yes")# 6341
sum(hosts$verbatim=="Yes")/nrow(hosts)# 8.2% of host-abstract combinations have verbatim mentions

length(unique(hosts$absID[hosts$verbatim=="Yes"]))# 5,051

# View(hosts[hosts$verbatim=="Yes",])

# View(hosts[hosts$verbatim=="No",])
hosts$HostName[hosts$verbatim=="No"] %>% tolower() %>% sort() %>% unique() %>% View()

hosts$HostName[hosts$verbatim=="No"] %>% tolower() %>% table() %>% sort() %>% rev() %>% View()

verb_host_absIDs <- hosts$absID[hosts$verbatim=="Yes"]
verb_para_absIDs <- paras$absID[hosts$verbatim=="Yes"]

abs_with_verbatim_sp <- data.frame(sort(intersect(verb_host_absIDs,verb_para_absIDs)))
names(abs_with_verbatim_sp) <- "absID"

write.csv(abs_with_verbatim_sp, "../raw_data/abs_with_verbatim_names.csv", row.names=F)