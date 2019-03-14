library(FactoMineR)
library(factoextra)

load("C:/Users/rikka/ESS3.RData")



dim(ESS3)
names(ESS3)

col.names=names(ESS3)
col.names <- col.names[which(col.names!="agea")]
ESS3[col.names] <- lapply(ESS3[col.names] , as.factor)
agea=as.integer(agea)
attach(ESS3)

table(cntry)
class(gndr)
table(gndr)
hist(agea)
table(eisced)
summary(ESS3)


data.MCA.1=ESS3[,c("gndr" ,   "agea"  ,  "eisced" , "ipcrtiv" ,"imprich", "ipeqopt", "ipshabt" ,"impsafe", "impdiff","ipfrule")]


MCA1=MCA(data.MCA.1, ncp = 5, ind.sup = NULL, quanti.sup = 2 ,quali.sup = c(1,3), excl=NULL, graph = TRUE)
var<-get_mca_var(MCA1)

head(get_eig(MCA1), 100)

fviz_eig(MCA1, choice="variance", labels=TRUE)
fviz_mca_var(MCA1, axes=c(1,2), choice = "mca.cor", repel = TRUE)
fviz_cos2(MCA1, choice = "var", axes = c(1,2,3))
fviz_mca_var(MCA1, axes=c(1,2), col.var = "cos2", repel = TRUE)
fviz_mca_ind(MCA1, col.ind = "cos2", axes=c(1,2), geom=c("point"), repel=TRUE)
fviz_mca_var(MCA1, axes=c(1,2), geom=c("point", "text"), repel=TRUE
# res.hcpc<-HCPC(MCA1, nb.clust=4, graph = FALSE)
set.seed(123)
data.cluster= sample.int(n = nrow(data.MCA.1), size = floor(.10*nrow(data.MCA.1)), replace = F)
data.MCA.2<- data.MCA.1[data.cluster, ]
dim(data.MCA.2)
MCA2=MCA(data.MCA.2, ncp = 5, ind.sup = NULL, quanti.sup = 2 ,quali.sup = c(1,3), excl=NULL, graph = TRUE)
var2<-get_mca_var(MCA1)
MCA3.hcpc<-HCPC(MCA2, nb.clust=4, graph = FALSE)
plot.HCPC(MCA3.hcpc, axes=c(1,2), choice="map")
MCA4.hcpc<-HCPC(MCA2, nb.clust=3, graph = FALSE)
plot.HCPC(MCA3.hcpc, axes=c(1,2), choice="map")













