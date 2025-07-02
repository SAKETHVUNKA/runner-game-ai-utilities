using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class PlayerMovement : MonoBehaviour
{
    public float speed;
    public float JumpForce;
    public float TurnSpeed;
    public bool jump;
    public float Speedup;
    public bool carhit;
    public GameObject Panel;
    public int Multiplier;
    AudioSource Audio;
    public AudioClip[] clips;

    public bool isPaused = true;

    UdpClient client;
    int listenPort = 5005;
    IPEndPoint remoteEndPoint;

    // Use this for initialization
    void Start()
    {
        speed = 5.0f;
        TurnSpeed = 5.0f;
        JumpForce = 100.0f;
        Speedup = 10.0f;
        Multiplier = 1;
        Audio = GetComponent<AudioSource>();

        client = new UdpClient(listenPort);
        remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);
        
        PauseGame();
    }

    // Update is called once per frame
    void Update()
    {
        ListenForMessages();

        SpeedUp();

        transform.Translate(Vector3.forward * speed * Time.deltaTime);
        if (Audio.isPlaying == false && !jump)
        {
            Audio.clip = clips[0];
            Audio.Play();
        }
        if (Input.GetKey(KeyCode.A))
        {
            transform.Translate(Vector3.left * TurnSpeed * Time.deltaTime);
        }
        if (Input.GetKey(KeyCode.D))
        {
            transform.Translate(Vector3.right * TurnSpeed * Time.deltaTime);
        }
        if (Input.GetKey(KeyCode.Space) && !jump)
        {
            jump = true;
            GetComponent<Animator>().SetBool("Jump", true);
            GetComponent<Rigidbody>().AddForce(Vector3.up * JumpForce);
            Audio.clip = clips[1];
            Audio.Play();
        }

        if (Input.GetKey(KeyCode.P))
        {
            if (!isPaused)
            {
                isPaused = true;
                PauseGame();
            }
            else
            {
                ResumeGame();
                isPaused = false;
            }
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.collider.CompareTag("Road"))
        {
            jump = false;
            GetComponent<Animator>().SetBool("Jump", false);
        }
        if (collision.collider.CompareTag("Car") || collision.collider.CompareTag("Obstracle"))
        {
            carhit = true;
            GetComponent<Animator>().SetBool("CarHit", true);
            Panel.SetActive(true);
            speed = 0.0f;
            Audio.clip = clips[2];
            Audio.Play();
            Audio.volume = 1;
        }
    }

    private void SpeedUp()
    {
        Speedup = Speedup - 1 * Time.deltaTime;
        if (Speedup <= 0.1f && speed >= 1.0f)
        {
            Multiplier += 1;
            speed += 1;
            Speedup = 10.0f;
        }
    }

    void PauseGame()
    {
        Time.timeScale = 0;
    }

    void ResumeGame()
    {
        Time.timeScale = 1;
    }

    void ListenForMessages()
    {
        try
        {
            if (client.Available > 0)
            {
                byte[] receivedBytes = client.Receive(ref remoteEndPoint);
                if (receivedBytes.Length > 0)
                {
                    string message = Encoding.ASCII.GetString(receivedBytes);
                    Debug.Log("Received pose: " + message);

                    if (message == "Pause" && !isPaused)
                    {
                        isPaused = true;
                        PauseGame();
                    }
                    if (message == "Play" && isPaused)
                    {
                        ResumeGame();
                        isPaused = false;
                    }
                    if (message == "Jump" && !jump)
                    {
                        jump = true;
                        GetComponent<Animator>().SetBool("Jump", true);
                        GetComponent<Rigidbody>().AddForce(Vector3.up * JumpForce);
                        Audio.clip = clips[1];
                        Audio.Play();
                    }
                    if (message == "Right")
                    {
                        if (transform.position.x < 3.75)
                        {
                            // Move to the right by k units if not at the edge
                            transform.Translate(Vector3.right + new Vector3(3.75, 0, 0));
                        }
                    }
                    if (message == "Left")
                    {
                        if (transform.position.x > -3.75)
                        {
                            // Move to the left by k units if not at the edge
                            transform.Translate(Vector3.right - new Vector3(3.75, 0, 0));
                        }
                    }
                }
            }
        }
        catch (Exception e)
        {
            Debug.Log(e.ToString());
        }
    }

    void OnApplicationQuit()
    {
        client.Close();
    }
}