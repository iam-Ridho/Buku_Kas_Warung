// Pembulatan dan format uang, disimpan sebagai nilai integer
int divRound(int n, int d) {
   if (d <= 0) {
    throw ArgumentError.value(d, "d", "pembagi harus > 0");
   }
   final q = n ~/ d;
   final r = n.remainder(d);
   
}