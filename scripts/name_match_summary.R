# name_match_summary.R

require(dplyr)

dat <- read.delim("../raw_data/hp_metadata.tsv", sep="\t")
abst <- read.delim("../raw_data/hp_abstracts.tsv", sep="\t", quote = "")

# View(dat[is.na(dat$ParasiteName),])
#these all seem to be Shaw with no data, however the pmids don't seem to be in the original Shaw database... where did these come from?

names(dat)
names(abst) <- c("abs","absID")

# parasites
paras <- left_join(select(dat, Parasite_original, absID), abst) %>% unique()

# View(paras[is.na(paras$Parasite_original),])

# identify abstracs with missing metadata 
missing <- paras$absID[is.na(paras$Parasite_original)]

# remove abstracts with NA for parasite name
paras <- paras[!is.na(paras$Parasite_original),]

length(missing)
length(intersect(paras$absID, missing))
# View(paras[paras$absID %in% missing,])
# these missing absID are represented with metadata... go back to original data and clean this.

paras <- paras %>% 
  rowwise() %>% 
  mutate(verbatim = if_else(any(grepl(Parasite_original, abs, ignore.case=TRUE)), "Yes", "No"))

sum(paras$verbatim=="Yes")# 55,363
sum(paras$verbatim=="Yes")/nrow(paras)# 70% of pathogen-abstract combinations have verbatim mentions

length(unique(paras$absID[paras$verbatim=="Yes"]))# 45,375 abstracts


# hosts
hosts <- left_join(select(dat, Host, Host_original, absID), abst) %>% unique()

# if Host_original is missing, swap in host name
hosts$HostName <- hosts$Host_original
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

sum(hosts$verbatim=="Yes")# 7008
sum(hosts$verbatim=="Yes")/nrow(hosts)# 8.9% of host-abstract combinations have verbatim mentions

length(unique(hosts$absID[hosts$verbatim=="Yes"]))# 5,126

# View(hosts[hosts$verbatim=="Yes",])

# View(hosts[hosts$verbatim=="No",])
hosts$HostName[hosts$verbatim=="No"] %>% tolower() %>% sort() %>% unique() %>% View()

hosts$HostName[hosts$verbatim=="No"] %>% tolower() %>% table() %>% sort() %>% rev() %>% View()

verb_host_absIDs <- hosts$absID[hosts$verbatim=="Yes"]
verb_para_absIDs <- paras$absID[hosts$verbatim=="Yes"]

abs_with_verbatim_sp <- data.frame(sort(intersect(verb_host_absIDs,verb_para_absIDs)))
names(abs_with_verbatim_sp) <- "absID"

abs_with_verbatim_sp

write.csv(abs_with_verbatim_sp, "../raw_data/abs_with_verbatim_names.csv", row.names=F)


# subset to exclude EID2 abstracts
eid2 <- dat[dat$Database%in%"EID2",]

abs_with_verbatim_noEID2 <- setdiff(abs_with_verbatim_sp$absID, eid2$absID)
length(abs_with_verbatim_noEID2)#672

dat_noeid <- dat[!dat$absID%in%eid2$absID,]

dat_test <- dat_noeid[dat_noeid$absID%in%abs_with_verbatim_noEID2,]
