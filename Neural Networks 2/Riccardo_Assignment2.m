% IS53002B Neural Networks
% Assignment 2
% Gastone Riccardo Tolli
% ID: 33506151
% Date: 23/04/2018
% using Haykin book pg 224 equation 4.108 and 4.121 in section 4.18


%Matlab version R2017b

clear all;

%load in sunspot data
load sunspot.dat


Epochs = 100; % this is for the algorithm later
%Newtons Method
% Putting the years and the values from the data loaded in above into
% variables
Sspot=sunspot(:,2);
Years=sunspot(:,1); 
% Normalization of the values
Sigma=std(Sspot(:));
Mu=mean(Sspot(:)); 





Normalization=(Sspot(:)-Mu)./Sigma;
Min=min(Normalization(:));
Max=max(Normalization(:));
Sspot=2.0*((Normalization-Min)/(Max-Min)-0.5);
% Laying down inputs/outs
xx=10;
SSpotTrans=Sspot';
xxx=length(SSpotTrans)-xx;


% matrix with lagged values in order to do the time series
for i=1:xxx
   b(i)=SSpotTrans(i+xx);
   
   for kk=1:xx
       c(i,kk) = SSpotTrans(i-kk+xx); 
       
   end
end
lay1 = 5; I = c';
O = b;
[INu,P1n] = size(I); 
[ONu,p2n] = size(O);


obs= [I;ones(1,P1n)]; %observations
WW1 = 0.5*(rand(lay1,1+INu)-0.5);  % Random weights
WW2 = 0.5*(rand(1,1+lay1)-0.5);   
gdh = (xx + 1) * lay1;% Gradient descent with Hessian
HH = zeros(gdh + lay1+1);
GG = zeros(1, gdh + lay1+1); 

 
% Going into algorithm for the weights
%Plot
Plot1 = plot(nan, '--');
hold on

for e = 1:Epochs
    
    % gradient descent
    for i = 1:P1n 
        GI1 = WW1 * obs(:,i); % fwd pass|| imput later ->hidden
        Lay1G = sigmoid(GI1);
        OG1 = [Lay1G; ones(1)];% hidden->out
        OutG = WW2 * OG1;
        BG = O(:,i) - OutG;  %start bkwd pass ||Betas
        EG = ( WW2' * BG ); % error of gradient
        BOG = Lay1G .* (1.0 - Lay1G) .* EG(1:end-1,:); % Beta out gradient
        DW2G = BG * OG1';  % deltas
        DW1G = BOG * obs(:,i)';
  
        % Reshaping Gradient
        DW1G = reshape(DW1G, [1, gdh]);
        Z = [DW2G,DW1G]; 
        GG = GG + Z;
    end
    
    
    % hessian
    for i = 1:P1n 
        I1H = WW1 * obs(:,i);  %fwd pass input -> hidden
        Hlay1 = sigmoid(I1H);
        OHE1 = [Hlay1; ones(1)];  %hidden->output
        OHE = WW2 * OHE1; 
        ERRHESS = O(:,i) - OHE;  %bkwd pass || Betas
        BHESS = 1;
        ERRHESS2 = ( WW2' * BHESS );
        HBout = Hlay1 .* (1.0 - Hlay1) .* ERRHESS2(1:end-1,:);
        DW2Hess = BHESS * OHE1'; %deltas 
        DW1HESS = HBout * obs(:,i)';
        DW1HESS = reshape(DW1HESS, [1, gdh]); % Finalizing Hessian
        PPHESS = [DW2Hess,DW1HESS];  
        QQHESS = PPHESS' * PPHESS;
        HH = HH + QQHESS;
    end
    HH = 1/P1n * HH; % new weights   
    GG = 1/P1n * GG;  
    HII = 0.0001 *eye(size(HH)); % identity matrix
    HH = HH + HII;     
    
    
    
    
    
    
    
    
    TotDW = inv(HH) * GG';
    DDWW2 = TotDW(1:6,:);  % dimention shift
    DDWW1 = reshape(TotDW(7:end,:),[5,11]); 
 
    WW1 = WW1 + DDWW1; % new w
    WW2 = WW2 + DDWW2';% new w
    

    
    
    
    
    
    
    
    
    
    
    
    INS1 = WW1 * obs; % applying new weights|| In -> hidden
    lay1 = sigmoid(INS1);
    Out1 = [lay1; ones(1, P1n)]; % hidden-> Out
    OOT = WW2 * Out1; % outputs
    ERRR = O - OOT; % errors
    MSE = sum(ERRR.^2)/P1n; % performance as MSE
    epoch(e, :) = e; % 
    mse(e, :) = MSE;
    set(Plot1, 'YData', mse)
    set(Plot1, 'XData', epoch)
    drawnow()
 
end
 
 


function y = sigmoid(x)
    y = 1 ./ (1 + exp(-x)) ;
end

