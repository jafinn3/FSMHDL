`default_nettype none;


/* * * * * * * * * * *
 *    testModule     *
 * * * * * * * * * * */
module testModule (
  input  logic in,
  output logic out);

  logic in1, in2, in3, out1, out2;
  testFSM fsm (in1, in2, in3, out1, out2);

endmodule: testModule

/* * * * * * * * * * *
 *      testFSM      *
 * * * * * * * * * * *
 *
 * Here is a sample module to highlight the syntax 
 * of our FSM HDL.
 */
$fsm testFSM (
  input  logic in1, in2, in3,
  output logic out1, out2);

  /* Declares all possible states in the FSM */
  $states init, read1, read2, read3
      read4, read5, read6;


  /* Define all possible transitions */
  $transitions begin
    init -> read1: in1 & in2;
    init -> read2: in1 & ~in2;
    read1 -> read1: in3;
    read1 -> init: in2 & ~in3;
    read2 -> read3: in1 | in2 | in3;
    read3 -> init: 1;
  end

  /* Define asserted outputs if the FSM is a moore machine. */
  $moore_out begin
    init: out1;
    read1: out2;
    read2: out2, out1;
    read3: out2, out1;

    /* Specify default output values (optional) */
    default: begin
      //out1 = 0;
      //out2 = 0;
      ~out1, ~out2;
    end
  end

  /* Define asserted outputs if the FSM is a mealy machine */
  $mealy_out begin
    init -> read1: out1;
    init -> read2: out2 = in1; // There might be a nicer way of doing something
                               // like this. 
    read1 -> read1: out1, out2;
    read3 -> init: out1 = in1, out2;
  end
$endfsm