%DATA:

%Training Set
             
              %x1 x2 Out              
Observation1 = [1,1,0] ; %example1
Observation2 = [1,0,1] ; %example2
              
              
%Initial weights

Weights = [0.2,-0.1,0.15,-0.1,-0.2,0.3,-0.2,0.1,0.2];
           %w1  w2   w3   w4   w5  w6   w7  w8  w9

%Epochs           
Epochs=100;

%learning rate
lr=1;

%NEURAL NETWORK;

%loop for the number of epochs

for epoch = 2%(1:Epochs)/2
    
    %Forward Pass example 1
    
    y1= sigmoid(Observation1(1)*Weights(1));
    y2= sigmoid((Observation1(1)*Weights(3))+(Observation1(2)*Weights(4)));
    y3= sigmoid(Observation1(2)*Weights(6));
    OUT= (y1*Weights(9))+(Observation1(1)*Weights(2))+(y2*Weights(8))+(Observation1(2)*Weights(5))+(y3*Weights(7));

    %Backward Pass example 1
    
    %Error Rates:
    
    BetaOUT = Observation1(3)-OUT;
    BetaSig1 = y1*(1-y1)*(BetaOUT)*Weights(9);
    BetaSig2 = y2*(1-y2)*(BetaOUT)*Weights(8);
    BetaSig3 = y3*(1-y3)*(BetaOUT)*Weights(7);

    %Deltas
    
    Deltaw9= lr*BetaOUT*y1;
    Deltaw8= lr*BetaOUT*y2;
    Deltaw7= lr*BetaOUT*y3;
    Deltaw2= lr*BetaOUT*Observation1(1);
    Deltaw5= lr*BetaOUT*Observation1(2);
    Deltaw1= lr*BetaSig1*Observation1(1);
    Deltaw3= lr*BetaSig2*Observation1(1);
    Deltaw4= lr*BetaSig2*Observation1(2);
    Deltaw6= lr*BetaSig3*Observation1(2);
    Deltas=[Deltaw1,Deltaw2,Deltaw3,Deltaw4,Deltaw5,Deltaw6,Deltaw7,Deltaw8,Deltaw9];

    %Weights Update
    
    for n= 1:size(Weights,2)
        Weights(n)=Weights(n)+ Deltas(n);
    end
    
    %Returning the weights, the output and the Squared Error for each epoch
    
    Weights
    OUT
    Squared_Error =(Observation1(3)-OUT)^2
    
    
    %Forward Pass example 2
    
    y1= sigmoid(Observation2(1)*Weights(1));
    y2= sigmoid((Observation2(1)*Weights(3))+(Observation2(2)*Weights(4)));
    y3= sigmoid(Observation2(2)*Weights(6));
    OUT= (y1*Weights(9))+(Observation2(1)*Weights(2))+(y2*Weights(8))+(Observation2(2)*Weights(5))+(y3*Weights(7));

    %Backward Pass example 2
   
    %Error Rates:
    
    BetaOUT = Observation2(3)-OUT;
    BetaSig1 = y1*(1-y1)*(BetaOUT)*Weights(9);
    BetaSig2 = y2*(1-y2)*(BetaOUT)*Weights(8);
    BetaSig3 = y3*(1-y3)*(BetaOUT)*Weights(7);

    %Deltas
    
    Deltaw9= lr*BetaOUT*y1;
    Deltaw8= lr*BetaOUT*y2;
    Deltaw7= lr*BetaOUT*y3;
    Deltaw2= lr*BetaOUT*Observation2(1);
    Deltaw5= lr*BetaOUT*Observation2(2);
    Deltaw1= lr*BetaSig1*Observation2(1);
    Deltaw3= lr*BetaSig2*Observation2(1);
    Deltaw4= lr*BetaSig2*Observation2(2);
    Deltaw6= lr*BetaSig3*Observation2(2);
    Deltas=[Deltaw1,Deltaw2,Deltaw3,Deltaw4,Deltaw5,Deltaw6,Deltaw7,Deltaw8,Deltaw9];

    %Weights Update
   
    for n= 1:size(Weights,2)
        Weights(n)=Weights(n)+ Deltas(n);
    end
    
    %Returning the weights, the output and the Squared Error for each epoch
    
    Weights
    OUT
    Squared_Error =(Observation2(3)-OUT)^2
end

%fprintf("The final results at the 100th epoch are:\n Weights : w1=%0.4f  w2=%0.4f  w3=%0.4f  w4=%0.4f  w5=%0.4f  w6=%0.4f  w7=%0.4f  w8=%0.4f  w9=%0.4f \n Squared Error=%0.4f  \n",Weights(1),Weights(2),Weights(3),Weights(4),Weights(5),Weights(6),Weights(7),Weights(8),Weights(9),Squared_Error)

