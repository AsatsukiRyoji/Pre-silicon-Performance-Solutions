// Cache Testbench
// Testbench for cache functionality testing

module cache_tb;
    // Test parameters
    parameter int unsigned SEED = 12345;
    parameter int unsigned TIMEOUT = 1000000;
    
    // Clock and reset signals
    logic clk;
    logic rst_n;
    
    // Test control
    logic test_start;
    logic test_done;
    logic test_pass;
    
    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    // Reset generation
    initial begin
        rst_n = 0;
        #100 rst_n = 1;
    end
    
    // Test stimulus
    initial begin
        // Initialize signals
        test_start = 0;
        test_done = 0;
        test_pass = 0;
        
        // Wait for reset
        @(posedge clk);
        @(posedge clk);
        
        // Start test
        test_start = 1;
        @(posedge clk);
        test_start = 0;
        
        // Run cache sanity test
        cache_sanity_test sanity_test();
        
        // Wait for test completion
        wait(test_done);
        
        // Check result
        if (test_pass) begin
            $display("** TEST PASSED **");
        end else begin
            $display("** TEST FAILED **");
        end
        
        $finish;
    end
    
    // Timeout
    initial begin
        #TIMEOUT;
        $display("** TEST TIMEOUT **");
        $finish;
    end
    
    // Instantiate cache sanity test
    cache_sanity_test dut (
        .clk(clk),
        .rst_n(rst_n)
    );
    
endmodule
